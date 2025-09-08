"""
PDF Report Generator for NFL Fantasy League
Creates weekly dashboard reports with winners, statistics, and standings
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import sqlite3
from typing import List, Dict, Any
import io

class WeeklyDashboardPDF:
    """Generate PDF reports for weekly fantasy league dashboard"""
    
    def __init__(self, db_path: str = 'nfl_fantasy.db'):
        self.db_path = db_path
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen
        )

    def get_weekly_data(self, week: int, year: int) -> Dict[str, Any]:
        """Get all data needed for weekly dashboard PDF"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get weekly leaderboard data - FIXED to only count games from the specified week
        cursor.execute('''
            SELECT u.username,
                   COUNT(CASE WHEN p.is_correct = 1 AND g.week = ? AND g.year = ? THEN 1 END) as games_won,
                   COUNT(CASE WHEN p.is_correct = 0 AND g.week = ? AND g.year = ? THEN 1 END) as games_lost,
                   COUNT(CASE WHEN g.is_final = 1 AND g.week = ? AND g.year = ? THEN 1 END) as games_played,
                   COUNT(CASE WHEN g.week = ? AND g.year = ? THEN p.id END) as total_picks,
                   ROUND(
                       CASE 
                           WHEN COUNT(CASE WHEN g.is_final = 1 AND g.week = ? AND g.year = ? THEN 1 END) > 0
                           THEN CAST(COUNT(CASE WHEN p.is_correct = 1 AND g.week = ? AND g.year = ? THEN 1 END) AS FLOAT) * 100.0 / 
                                COUNT(CASE WHEN g.is_final = 1 AND g.week = ? AND g.year = ? THEN 1 END)
                           ELSE 0 
                       END, 1
                   ) as win_percentage,
                   -- Monday Night tiebreaker info
                   (SELECT predicted_home_score + predicted_away_score
                    FROM user_picks up2
                    JOIN nfl_games g2 ON up2.game_id = g2.id
                    WHERE up2.user_id = u.id AND g2.week = ? AND g2.year = ? 
                    AND g2.is_monday_night = 1 LIMIT 1) as monday_total_prediction,
                   (SELECT predicted_home_score || '–' || predicted_away_score
                    FROM user_picks up2
                    JOIN nfl_games g2 ON up2.game_id = g2.id
                    WHERE up2.user_id = u.id AND g2.week = ? AND g2.year = ? 
                    AND g2.is_monday_night = 1 LIMIT 1) as monday_score_prediction
            FROM users u
            LEFT JOIN user_picks p ON u.id = p.user_id
            LEFT JOIN nfl_games g ON p.game_id = g.id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.username
            HAVING COUNT(CASE WHEN g.week = ? AND g.year = ? THEN p.id END) > 0
            ORDER BY games_won DESC, win_percentage DESC, monday_total_prediction ASC, u.username
        ''', (week, year, week, year, week, year, week, year, week, year, week, year, week, year, week, year, week, year, week, year))
        
        leaderboard = [dict(row) for row in cursor.fetchall()]
        
        # Get game status summary
        cursor.execute('''
            SELECT 
                COUNT(*) as total_games,
                COUNT(CASE WHEN is_final = 1 THEN 1 END) as final_games,
                COUNT(CASE WHEN is_final = 0 THEN 1 END) as pending_games
            FROM nfl_games 
            WHERE week = ? AND year = ?
        ''', (week, year))
        
        game_summary = dict(cursor.fetchone())
        
        # Get individual game results
        cursor.execute('''
            SELECT away_team, home_team, away_score, home_score, game_status, is_final,
                   CASE 
                       WHEN is_thursday_night = 1 THEN 'Thursday Night'
                       WHEN is_monday_night = 1 THEN 'Monday Night'
                       WHEN is_sunday_night = 1 THEN 'Sunday Night'
                       ELSE 'Regular'
                   END as game_type
            FROM nfl_games 
            WHERE week = ? AND year = ?
            ORDER BY game_date
        ''', (week, year))
        
        games = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'leaderboard': leaderboard,
            'game_summary': game_summary,
            'games': games,
            'week': week,
            'year': year,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def create_leaderboard_table(self, leaderboard: List[Dict]) -> Table:
        """Create the main leaderboard table"""
        # Table headers
        headers = ['Rank', 'Player', 'Wins', 'Losses', 'Win %', 'Monday Night']
        
        # Table data
        data = [headers]
        
        for i, player in enumerate(leaderboard, 1):
            rank_emoji = ''
            if i == 1:
                rank_emoji = '🥇'
            elif i == 2:
                rank_emoji = '🥈'
            elif i == 3:
                rank_emoji = '🥉'
            
            row = [
                f"{rank_emoji} {i}",
                player['username'].title(),
                str(player['games_won'] or 0),
                str(player['games_lost'] or 0),
                f"{player['win_percentage'] or 0}%",
                player['monday_score_prediction'] or 'No pick'
            ]
            data.append(row)
        
        # Create table
        table = Table(data, colWidths=[0.8*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Winner highlighting
            ('BACKGROUND', (0, 1), (-1, 1), colors.gold),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
        ]))
        
        return table

    def create_game_summary_table(self, game_summary: Dict, games: List[Dict]) -> Table:
        """Create game status summary table"""
        headers = ['Game', 'Matchup', 'Score', 'Status']
        data = [headers]
        
        for game in games:
            matchup = f"{game['away_team']} @ {game['home_team']}"
            
            if game['is_final']:
                score = f"{game['away_score']}-{game['home_score']}"
                status = "FINAL"
            else:
                score = "TBD"
                status = game['game_status'].title()
            
            data.append([
                game['game_type'],
                matchup,
                score,
                status
            ])
        
        table = Table(data, colWidths=[1.2*inch, 2*inch, 1*inch, 1*inch])
        
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightblue]),
        ]))
        
        return table

    def generate_pdf(self, week: int, year: int) -> bytes:
        """Generate PDF report and return as bytes"""
        # Get data
        data = self.get_weekly_data(week, year)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        
        # Build story
        story = []
        
        # Title
        title = Paragraph(f"🏈 La Casa de Todos - Week {week} Dashboard", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Summary stats
        summary_text = f"""
        <b>Week {week}, {year} Summary</b><br/>
        Total Games: {data['game_summary']['total_games']}<br/>
        Final Games: {data['game_summary']['final_games']}<br/>
        Pending Games: {data['game_summary']['pending_games']}<br/>
        Generated: {data['generated_at']}
        """
        summary = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 20))
        
        # Leaderboard section
        leaderboard_heading = Paragraph("🏆 Weekly Leaderboard", self.heading_style)
        story.append(leaderboard_heading)
        
        if data['leaderboard']:
            leaderboard_table = self.create_leaderboard_table(data['leaderboard'])
            story.append(leaderboard_table)
        else:
            no_data = Paragraph("No picks data available for this week.", self.styles['Normal'])
            story.append(no_data)
        
        story.append(Spacer(1, 30))
        
        # Games section
        games_heading = Paragraph("🎯 Week Games Status", self.heading_style)
        story.append(games_heading)
        
        if data['games']:
            games_table = self.create_game_summary_table(data['game_summary'], data['games'])
            story.append(games_table)
        else:
            no_games = Paragraph("No games scheduled for this week.", self.styles['Normal'])
            story.append(no_games)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

def generate_weekly_dashboard_pdf(week: int, year: int = 2025, db_path: str = 'nfl_fantasy.db') -> bytes:
    """Convenience function to generate weekly dashboard PDF"""
    generator = WeeklyDashboardPDF(db_path)
    return generator.generate_pdf(week, year)
