#!/usr/bin/env python3
"""
La Casa de Todos NFL Fantasy League - Bilingual User Guide PDF Generator
Creates a friendly PDF guide for new users in English and Spanish with screenshots
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os

# Bilingual content dictionary
CONTENT = {
    'en': {
        'title': '🏠 La Casa de Todos',
        'subtitle': 'NFL Fantasy League',
        'guide_title': 'Family Edition User Guide',
        'welcome': """
        Welcome to La Casa de Todos NFL Fantasy League! This friendly guide will help you get started 
        with our family-focused fantasy football system. Whether you're new to fantasy sports or a 
        seasoned player, this guide covers everything you need to know to participate and have fun!
        """,
        'toc_title': '📋 Table of Contents',
        'toc_items': [
            "1. Getting Started - First Login",
            "2. Making Your Picks", 
            "3. Managing Your Profile",
            "4. Understanding the Leaderboards",
            "5. Rules and Scoring",
            "6. Tips for Success",
            "7. Troubleshooting & Support"
        ],
        'getting_started': '1. 🚀 Getting Started - First Login',
        'default_login': 'Default Login Credentials',
        'important_password': """
        <b>IMPORTANT:</b> All new users start with the default password <b>'1234'</b>. 
        Please change this immediately after your first login for security!
        """,
        'login_steps_title': 'Step-by-Step First Login:',
        'website_url': 'https://casadetodos.eastus.cloudapp.azure.com/',
        'login_steps': [
            "1. Open your web browser and go to: <b>https://casadetodos.eastus.cloudapp.azure.com/</b>",
            "2. Click the 'Login' button or link", 
            "3. Enter your assigned username (ask the admin if you don't know it)",
            "4. Enter the default password: <b>1234</b>",
            "5. Click 'Login' to access the system",
            "6. You'll be taken to the main dashboard"
        ],
        'after_login': 'What You\'ll See After Login:',
        'dashboard_info': """
        After logging in, you'll see the main dashboard with:
        • Navigation menu with Dashboard, Make Picks, Leaderboards, Rules, My Profile, and Logout
        • Current week information and deadlines
        • Your recent picks and scores
        • Quick links to important features
        """,
        'making_picks': '2. 🏈 Making Your Picks',
        'how_game_works': 'How the Game Works:',
        'game_explanation': """
        Each week, you'll pick the winning team for every NFL game. It's simple - just choose 
        which team you think will win each matchup. You earn 1 point for every correct pick.
        """,
        'picks_steps_title': 'Making Your Weekly Picks:',
        'picks_steps': [
            "1. Click 'Make Picks' in the navigation menu",
            "2. You'll see all games for the current week",
            "3. For each game, click on the team you think will win",
            "4. For Monday Night Football, also predict the total score (used for tiebreakers)",
            "5. Review your picks to make sure they're all selected",
            "6. Click 'Submit Picks' to save them",
            "7. You can change your picks until the deadline for each game"
        ],
        'deadlines': 'Important Deadlines:',
        'deadline_info': """
        <b>Thursday Games:</b> Picks must be submitted before Thursday 8:00 PM ET<br/>
        <b>Sunday Games:</b> Picks must be submitted before Sunday 1:00 PM ET<br/>
        <b>Monday Night Football:</b> Picks must be submitted before Monday 8:00 PM ET<br/>
        <br/>
        ⚠️ <b>Warning:</b> You cannot change your picks after these deadlines!
        """,
        'profile_management': '3. 👤 Managing Your Profile',
        'accessing_profile': 'Accessing Your Profile:',
        'profile_access_info': "Click 'My Profile' in the navigation menu to access your personal settings.",
        'changing_password': 'Changing Your Password (IMPORTANT!):',
        'password_steps': [
            "1. Go to 'My Profile' page",
            "2. Scroll down to the 'Change Password' section",
            "3. Enter your current password (initially '1234')",
            "4. Enter your new password (must be at least 6 characters)",
            "5. Confirm your new password by typing it again",
            "6. Click 'Save Changes'",
            "7. You'll see a success message when it's updated"
        ],
        'favorite_team': 'Setting Your Favorite Team:',
        'team_steps': [
            "1. In your profile, find the 'Fantasy Preferences' section",
            "2. Click the dropdown menu under 'Favorite NFL Team'",
            "3. Select your favorite team from all 32 NFL teams",
            "4. Click 'Save Changes' to update your preference",
            "5. Your favorite team will be displayed on your profile"
        ],
        'team_tip': """
        <b>Pro Tip:</b> Setting your favorite team helps personalize your experience and shows 
        other family members which team you support!
        """,
        'conclusion': """
        We're excited to have you join our family fantasy football league! This system is designed 
        to be simple, fun, and bring the family together through friendly competition. If you have 
        any questions or suggestions for improvements, don't hesitate to reach out.
        
        Good luck with your picks, and may the best family member win! 🏈
        """
    },
    'es': {
        'title': '🏠 La Casa de Todos',
        'subtitle': 'Liga de Fantasía NFL',
        'guide_title': 'Guía del Usuario - Edición Familiar',
        'welcome': """
        ¡Bienvenido a La Casa de Todos Liga de Fantasía NFL! Esta guía amigable te ayudará a comenzar 
        con nuestro sistema de fútbol americano de fantasía enfocado en la familia. Ya seas nuevo en 
        los deportes de fantasía o un jugador experimentado, esta guía cubre todo lo que necesitas 
        saber para participar y divertirte!
        """,
        'toc_title': '📋 Tabla de Contenidos',
        'toc_items': [
            "1. Comenzando - Primer Inicio de Sesión",
            "2. Haciendo tus Selecciones",
            "3. Administrando tu Perfil", 
            "4. Entendiendo las Tablas de Posiciones",
            "5. Reglas y Puntuación",
            "6. Consejos para el Éxito",
            "7. Solución de Problemas y Soporte"
        ],
        'getting_started': '1. 🚀 Comenzando - Primer Inicio de Sesión',
        'default_login': 'Credenciales de Inicio de Sesión Predeterminadas',
        'important_password': """
        <b>IMPORTANTE:</b> Todos los usuarios nuevos comienzan con la contraseña predeterminada <b>'1234'</b>. 
        ¡Por favor cámbiala inmediatamente después de tu primer inicio de sesión por seguridad!
        """,
        'login_steps_title': 'Pasos para el Primer Inicio de Sesión:',
        'website_url': 'https://casadetodos.eastus.cloudapp.azure.com/',
        'login_steps': [
            "1. Abre tu navegador web y ve a: <b>https://casadetodos.eastus.cloudapp.azure.com/</b>",
            "2. Haz clic en el botón o enlace 'Login'",
            "3. Ingresa tu nombre de usuario asignado (pregunta al administrador si no lo sabes)",
            "4. Ingresa la contraseña predeterminada: <b>1234</b>",
            "5. Haz clic en 'Login' para acceder al sistema",
            "6. Serás llevado al panel principal"
        ],
        'after_login': 'Lo que Verás Después del Inicio de Sesión:',
        'dashboard_info': """
        Después de iniciar sesión, verás el panel principal con:
        • Menú de navegación con Panel, Hacer Selecciones, Tablas de Posiciones, Reglas, Mi Perfil y Cerrar Sesión
        • Información de la semana actual y fechas límite
        • Tus selecciones recientes y puntuaciones
        • Enlaces rápidos a características importantes
        """,
        'making_picks': '2. 🏈 Haciendo tus Selecciones',
        'how_game_works': 'Cómo Funciona el Juego:',
        'game_explanation': """
        Cada semana, elegirás el equipo ganador para cada juego de NFL. Es simple - solo elige 
        qué equipo crees que ganará cada enfrentamiento. Ganas 1 punto por cada selección correcta.
        """,
        'picks_steps_title': 'Haciendo tus Selecciones Semanales:',
        'picks_steps': [
            "1. Haz clic en 'Hacer Selecciones' en el menú de navegación",
            "2. Verás todos los juegos de la semana actual",
            "3. Para cada juego, haz clic en el equipo que crees que ganará",
            "4. Para el Fútbol del Lunes por la Noche, también predice el puntaje total (usado para desempates)",
            "5. Revisa tus selecciones para asegurarte de que todas estén elegidas",
            "6. Haz clic en 'Enviar Selecciones' para guardarlas",
            "7. Puedes cambiar tus selecciones hasta la fecha límite de cada juego"
        ],
        'deadlines': 'Fechas Límite Importantes:',
        'deadline_info': """
        <b>Juegos de Jueves:</b> Las selecciones deben enviarse antes del Jueves 8:00 PM ET<br/>
        <b>Juegos de Domingo:</b> Las selecciones deben enviarse antes del Domingo 1:00 PM ET<br/>
        <b>Fútbol del Lunes por la Noche:</b> Las selecciones deben enviarse antes del Lunes 8:00 PM ET<br/>
        <br/>
        ⚠️ <b>Advertencia:</b> ¡No puedes cambiar tus selecciones después de estas fechas límite!
        """,
        'profile_management': '3. 👤 Administrando tu Perfil',
        'accessing_profile': 'Accediendo a tu Perfil:',
        'profile_access_info': "Haz clic en 'Mi Perfil' en el menú de navegación para acceder a tu configuración personal.",
        'changing_password': 'Cambiando tu Contraseña (¡IMPORTANTE!):',
        'password_steps': [
            "1. Ve a la página 'Mi Perfil'",
            "2. Desplázate hacia abajo a la sección 'Cambiar Contraseña'",
            "3. Ingresa tu contraseña actual (inicialmente '1234')",
            "4. Ingresa tu nueva contraseña (debe tener al menos 6 caracteres)",
            "5. Confirma tu nueva contraseña escribiéndola de nuevo",
            "6. Haz clic en 'Guardar Cambios'",
            "7. Verás un mensaje de éxito cuando se actualice"
        ],
        'favorite_team': 'Configurando tu Equipo Favorito:',
        'team_steps': [
            "1. En tu perfil, encuentra la sección 'Preferencias de Fantasía'",
            "2. Haz clic en el menú desplegable bajo 'Equipo NFL Favorito'",
            "3. Selecciona tu equipo favorito de los 32 equipos de NFL",
            "4. Haz clic en 'Guardar Cambios' para actualizar tu preferencia",
            "5. Tu equipo favorito se mostrará en tu perfil"
        ],
        'team_tip': """
        <b>Consejo Pro:</b> ¡Configurar tu equipo favorito ayuda a personalizar tu experiencia y muestra 
        a otros miembros de la familia qué equipo apoyas!
        """,
        'conclusion': """
        ¡Estamos emocionados de tenerte en nuestra liga de fútbol americano de fantasía familiar! Este sistema está diseñado 
        para ser simple, divertido y unir a la familia a través de competencia amigable. Si tienes 
        alguna pregunta o sugerencias para mejoras, no dudes en contactarnos.
        
        ¡Buena suerte con tus selecciones, y que gane el mejor miembro de la familia! 🏈
        """
    }
}


def add_screenshot_placeholder(story, screenshot_name, caption_en, caption_es, language='en'):
    """Add a placeholder for screenshots with bilingual captions"""
    
    # Create screenshot placeholder
    screenshot_path = f"screenshots/{screenshot_name}.png"
    
    if os.path.exists(screenshot_path):
        try:
            # If screenshot exists, add it
            img = Image(screenshot_path, width=5*inch, height=3*inch)
            story.append(img)
        except:
            # If image fails to load, show placeholder
            story.append(Paragraph(f"[Screenshot: {screenshot_name}]", 
                         ParagraphStyle('ScreenshotPlaceholder', 
                                      parent=getSampleStyleSheet()['Normal'],
                                      alignment=TA_CENTER,
                                      backColor=HexColor('#f0f0f0'),
                                      borderColor=HexColor('#cccccc'),
                                      borderWidth=1,
                                      borderPadding=10)))
    else:
        # Show placeholder if screenshot doesn't exist
        story.append(Paragraph(f"[📸 Screenshot Placeholder: {screenshot_name}]", 
                     ParagraphStyle('ScreenshotPlaceholder',
                                  parent=getSampleStyleSheet()['Normal'],
                                  alignment=TA_CENTER,
                                  backColor=HexColor('#e8f4f8'),
                                  borderColor=HexColor('#667eea'),
                                  borderWidth=1,
                                  borderPadding=10,
                                  fontSize=10,
                                  textColor=HexColor('#667eea'))))
    
    # Add caption in selected language
    caption = caption_en if language == 'en' else caption_es
    story.append(Paragraph(f"<i>{caption}</i>", 
                 ParagraphStyle('Caption',
                              parent=getSampleStyleSheet()['Normal'],
                              alignment=TA_CENTER,
                              fontSize=9,
                              textColor=HexColor('#666666'),
                              spaceAfter=15)))


def create_bilingual_user_guide_pdf():
    """Create a comprehensive bilingual user guide PDF with screenshot support"""
    
    # Create directory for screenshots if it doesn't exist
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
        print("📁 Created 'screenshots' directory - add your screenshot images here!")
    
    # Create the PDF document
    filename = "La_Casa_de_Todos_Bilingual_User_Guide.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                          leftMargin=0.75*inch, rightMargin=0.75*inch,
                          topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#2c3e50'),
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=HexColor('#34495e'),
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=HexColor('#667eea'),
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    step_style = ParagraphStyle(
        'StepStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    highlight_style = ParagraphStyle(
        'HighlightStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        backColor=HexColor('#f8f9fa'),
        borderColor=HexColor('#667eea'),
        borderWidth=1,
        borderPadding=10,
        fontName='Helvetica-Bold'
    )
    
    # Story list to hold all content
    story = []
    
    # Create both English and Spanish versions
    for lang in ['en', 'es']:
        content = CONTENT[lang]
        
        # Language indicator
        lang_title = "English Version" if lang == 'en' else "Versión en Español"
        story.append(Paragraph(f"📖 {lang_title}", subheading_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Title page
        story.append(Paragraph(content['title'], title_style))
        story.append(Paragraph(content['subtitle'], title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(content['guide_title'], heading_style))
        story.append(Spacer(1, 0.5*inch))
        
        # Welcome message
        story.append(Paragraph(content['welcome'], normal_style))
        
        # Website URL section
        website_title = "🌐 Website Access" if lang == 'en' else "🌐 Acceso al Sitio Web"
        story.append(Paragraph(website_title, subheading_style))
        
        website_text = f"Visit La Casa de Todos at: <b>{content['website_url']}</b>" if lang == 'en' else f"Visita La Casa de Todos en: <b>{content['website_url']}</b>"
        story.append(Paragraph(website_text, highlight_style))
        
        story.append(Spacer(1, 0.3*inch))
        date_text = f"Guide created: {datetime.now().strftime('%B %d, %Y')}" if lang == 'en' else f"Guía creada: {datetime.now().strftime('%d de %B, %Y')}"
        story.append(Paragraph(date_text, normal_style))
        story.append(PageBreak())
        
        # Table of Contents
        story.append(Paragraph(content['toc_title'], heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        for item in content['toc_items']:
            story.append(Paragraph(item, step_style))
        
        story.append(PageBreak())
        
        # Section 1: Getting Started
        story.append(Paragraph(content['getting_started'], heading_style))
        
        story.append(Paragraph(content['default_login'], subheading_style))
        story.append(Paragraph(content['important_password'], highlight_style))
        
        # Add login screenshot placeholder
        add_screenshot_placeholder(story, "login_page", 
                                 "Login page showing username and password fields",
                                 "Página de inicio de sesión mostrando campos de usuario y contraseña", 
                                 lang)
        
        story.append(Paragraph(content['login_steps_title'], subheading_style))
        
        for step in content['login_steps']:
            story.append(Paragraph(step, step_style))
        
        story.append(Paragraph(content['after_login'], subheading_style))
        story.append(Paragraph(content['dashboard_info'], normal_style))
        
        # Add dashboard screenshot placeholder
        add_screenshot_placeholder(story, "dashboard", 
                                 "Main dashboard view after successful login",
                                 "Vista del panel principal después del inicio de sesión exitoso", 
                                 lang)
        
        story.append(PageBreak())
        
        # Section 2: Making Your Picks
        story.append(Paragraph(content['making_picks'], heading_style))
        
        story.append(Paragraph(content['how_game_works'], subheading_style))
        story.append(Paragraph(content['game_explanation'], normal_style))
        
        story.append(Paragraph(content['picks_steps_title'], subheading_style))
        
        for step in content['picks_steps']:
            story.append(Paragraph(step, step_style))
        
        # Add picks page screenshot placeholder
        add_screenshot_placeholder(story, "make_picks", 
                                 "Make Picks page showing weekly games and team selection",
                                 "Página de Hacer Selecciones mostrando juegos semanales y selección de equipos", 
                                 lang)
        
        story.append(Paragraph(content['deadlines'], subheading_style))
        story.append(Paragraph(content['deadline_info'], highlight_style))
        
        story.append(PageBreak())
        
        # Section 3: Managing Your Profile
        story.append(Paragraph(content['profile_management'], heading_style))
        
        story.append(Paragraph(content['accessing_profile'], subheading_style))
        story.append(Paragraph(content['profile_access_info'], normal_style))
        
        # Add profile screenshot placeholder
        add_screenshot_placeholder(story, "profile_page", 
                                 "User profile page showing personal information and settings",
                                 "Página de perfil de usuario mostrando información personal y configuraciones", 
                                 lang)
        
        story.append(Paragraph(content['changing_password'], subheading_style))
        
        for step in content['password_steps']:
            story.append(Paragraph(step, step_style))
        
        story.append(Paragraph(content['favorite_team'], subheading_style))
        
        for step in content['team_steps']:
            story.append(Paragraph(step, step_style))
        
        # Add team selection screenshot placeholder
        add_screenshot_placeholder(story, "team_selection", 
                                 "Favorite team dropdown menu with NFL teams",
                                 "Menú desplegable de equipo favorito con equipos de NFL", 
                                 lang)
        
        story.append(Paragraph(content['team_tip'], highlight_style))
        
        story.append(PageBreak())
        
        # Leaderboards section
        leaderboard_title = "4. 🏆 Understanding the Leaderboards" if lang == 'en' else "4. 🏆 Entendiendo las Tablas de Posiciones"
        story.append(Paragraph(leaderboard_title, heading_style))
        
        # Add leaderboard screenshot placeholder
        add_screenshot_placeholder(story, "season_leaderboard", 
                                 "Season leaderboard showing player rankings and scores",
                                 "Tabla de posiciones de temporada mostrando clasificaciones y puntuaciones de jugadores", 
                                 lang)
        
        add_screenshot_placeholder(story, "weekly_leaderboard", 
                                 "Weekly leaderboard with detailed pick results",
                                 "Tabla de posiciones semanal con resultados detallados de selecciones", 
                                 lang)
        
        story.append(PageBreak())
        
        # Footer section
        final_title = "🎉 Welcome to La Casa de Todos!" if lang == 'en' else "🎉 ¡Bienvenido a La Casa de Todos!"
        story.append(Paragraph(final_title, heading_style))
        story.append(Paragraph(content['conclusion'], normal_style))
        
        # Add separator between languages
        if lang == 'en':
            story.append(PageBreak())
            story.append(Paragraph("="*50, normal_style))
            story.append(PageBreak())
    
    # Build the PDF
    doc.build(story)
    
    return filename


def main():
    """Main function to create the bilingual user guide"""
    try:
        filename = create_bilingual_user_guide_pdf()
        print(f"✅ Bilingual user guide PDF created successfully: {filename}")
        print(f"📄 File size: {os.path.getsize(filename):,} bytes")
        print("📖 The PDF includes:")
        print("   🇺🇸 English version with:")
        print("      • Getting started with default login (password: 1234)")
        print("      • Step-by-step guide for making picks")
        print("      • How to change password and set favorite team")
        print("      • Understanding both leaderboards")
        print("      • Screenshot placeholders for visual guidance")
        print("   🇪🇸 Spanish version with:")
        print("      • Comenzando con inicio de sesión predeterminado (contraseña: 1234)")
        print("      • Guía paso a paso para hacer selecciones")
        print("      • Cómo cambiar contraseña y configurar equipo favorito")
        print("      • Entendiendo ambas tablas de posiciones")
        print("      • Marcadores de posición para capturas de pantalla")
        print("")
        print("📸 To add screenshots:")
        print("   • Create/place images in the 'screenshots/' folder")
        print("   • Supported images: login_page.png, dashboard.png, make_picks.png,")
        print("     profile_page.png, team_selection.png, season_leaderboard.png,")
        print("     weekly_leaderboard.png")
        print("   • Run the script again after adding images")
        
    except ImportError as e:
        print("❌ Error: Missing required library for PDF generation")
        print("💡 Please install reportlab: pip install reportlab")
        print(f"   Full error: {e}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("💡 Make sure you have write permissions in the current directory")


if __name__ == "__main__":
    main()
