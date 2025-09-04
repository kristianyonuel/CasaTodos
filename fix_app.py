#!/usr/bin/env python3

# Find the main section and replace it
import re

# Read the current file
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find where the main section starts
main_start = content.find('if __name__ == \'__main__\':')

if main_start != -1:
    # Keep everything before the main section
    before_main = content[:main_start]
    
    # Write the new main section
    new_main = '''if __name__ == '__main__':
    import os
    import ssl
    from werkzeug.serving import make_server
    
    # Initialize the database on startup
    initialize_app()
    
    # Simple SSL context setup for existing certificates
    def setup_ssl_context():
        """Setup SSL context using existing certificates"""
        try:
            # Look for standard SSL certificate files
            cert_files = [
                ('cert.pem', 'key.pem'),
                ('certificate.crt', 'private.key'),
                ('ssl_cert.pem', 'ssl_key.pem'),
                ('fullchain.pem', 'privkey.pem')  # Let's Encrypt format
            ]
            
            for cert_file, key_file in cert_files:
                if os.path.exists(cert_file) and os.path.exists(key_file):
                    logger.info(f"Using SSL certificates: {cert_file}, {key_file}")
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    context.load_cert_chain(cert_file, key_file)
                    return context
            
            logger.warning("No SSL certificates found. HTTPS will not be available.")
            return None
            
        except Exception as e:
            logger.error(f"Error setting up SSL: {e}")
            return None
    
    # Serve .well-known directory for SSL validation
    @app.route('/.well-known/<path:filename>')
    def wellknown(filename):
        """Serve files from .well-known directory for SSL validation"""
        try:
            return app.send_static_file(f'.well-known/{filename}')
        except:
            # If not in static, try current directory
            well_known_path = os.path.join('.well-known', filename)
            if os.path.exists(well_known_path):
                with open(well_known_path, 'r') as f:
                    return f.read(), 200, {'Content-Type': 'text/plain'}
            else:
                return 'File not found', 404
    
    # Determine run mode
    import sys
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'production'
    
    print("🏈 La Casa de Todos NFL Fantasy Server")
    print("=" * 50)
    
    if mode == 'dev':
        print("🛠️ Development Mode")
        print("📍 Access at: http://localhost:5000")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
        
    else:
        # Production mode - HTTP on 80, HTTPS on 443 if certificates available
        print("🚀 Production Mode")
        print("🌐 HTTP Server: Starting on port 80...")
        
        ssl_context = setup_ssl_context()
        if ssl_context:
            print("🔒 HTTPS Server: SSL certificates found, starting on port 443...")
        else:
            print("⚠️ HTTPS Server: No SSL certificates, HTTPS disabled")
        
        print("📍 Access URLs:")
        print("   🌐 HTTP:  http://your-domain.com")
        if ssl_context:
            print("   🔒 HTTPS: https://your-domain.com")
        print("💡 Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            # Start HTTP server
            http_server = make_server('0.0.0.0', 80, app, threaded=True)
            print("✅ HTTP server started on port 80")
            
            if ssl_context:
                # Start HTTPS server if SSL is available
                import threading
                
                def run_https():
                    try:
                        https_server = make_server('0.0.0.0', 443, app, ssl_context=ssl_context, threaded=True)
                        print("✅ HTTPS server started on port 443")
                        https_server.serve_forever()
                    except Exception as e:
                        logger.error(f"HTTPS server error: {e}")
                
                https_thread = threading.Thread(target=run_https, daemon=True)
                https_thread.start()
            
            # Run HTTP server in main thread
            http_server.serve_forever()
            
        except PermissionError:
            print("❌ Permission denied for ports 80/443")
            print("💡 Try running with sudo or use development mode:")
            print("   sudo python app.py production")
            print("   python app.py dev")
        except KeyboardInterrupt:
            print("\\n🛑 Shutting down servers...")
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"❌ Server error: {e}")
            print("💡 Try development mode: python app.py dev")
'''
    
    # Write the corrected file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(before_main + new_main)
    
    print("✅ Fixed app.py indentation error")
else:
    print("❌ Could not find main section in app.py")
