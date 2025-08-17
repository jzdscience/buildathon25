#!/usr/bin/env python3
"""
Quick verification script for Codebase Time Machine setup
"""

def verify_installation():
    print("🔍 Verifying Codebase Time Machine installation...")
    print("=" * 50)
    
    # Check Python version
    import sys
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check core dependencies
    required_imports = {
        'git': 'GitPython',
        'pandas': 'Pandas', 
        'matplotlib': 'Matplotlib',
        'plotly': 'Plotly',
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO'
    }
    
    missing = []
    for import_name, package_name in required_imports.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip3 install -r requirements.txt")
        return False
    
    # Check NLTK data
    try:
        import nltk
        from nltk.corpus import stopwords
        stopwords.words('english')
        print("✅ NLTK data")
    except:
        print("⚠️  NLTK data (optional)")
    
    # Test core functionality
    try:
        from codebase_time_machine import CodebaseTimeMachine
        tm = CodebaseTimeMachine()
        print("✅ Core analysis engine")
    except Exception as e:
        print(f"❌ Core analysis engine: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Installation verified successfully!")
    print("\n📋 Next steps:")
    print("1. Start web interface: python3 start_web.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Try the demo repositories")
    print("\n💡 Or use CLI: python3 codebase_time_machine.py --help")
    
    return True

if __name__ == "__main__":
    verify_installation()