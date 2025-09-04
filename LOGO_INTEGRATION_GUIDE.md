# 🎨 Logo Integration Guide for La Casa de Todos

## 📍 Where to Add Your Logo

I've set up **three perfect spots** where you can add your official logo in the login page:

### 🎯 **Primary Location (Currently Implemented)**
**Above the title in the login form** - This is the most professional and common placement.

## 🔧 How to Add Your Logo

### **Step 1: Prepare Your Logo**
1. **Recommended formats**: PNG (with transparency), SVG (scalable), or JPG
2. **Recommended size**: 80x80 pixels (square) or 120x60 pixels (rectangular)
3. **File name**: `logo.png`, `logo.svg`, or `logo.jpg`

### **Step 2: Place Your Logo File**
Put your logo file in: `static/images/logo.png`

```
La Casa de Todos/
├── static/
│   ├── images/
│   │   └── logo.png  ← Your logo goes here
│   ├── style.css
│   └── login.css
```

### **Step 3: Logo Styles Available**

The system automatically detects your logo and applies appropriate styling:

#### **For Round/Circular Logos:**
```html
<img src="..." class="logo">  <!-- Default: 80x80px, rounded -->
```

#### **For Square Logos:**
```html
<img src="..." class="logo square">  <!-- 70x70px, slightly rounded corners -->
```

#### **For Wide/Horizontal Logos:**
```html
<img src="..." class="logo wide">  <!-- 120x60px, rounded corners -->
```

#### **For Text-Based Logos:**
```html
<img src="..." class="logo text-logo">  <!-- Auto width, 50px height -->
```

## 🎨 **Alternative Logo Placement Options**

### **Option 2: Header with Logo + Text Side by Side**

Edit `templates/login.html` and replace the logo section:

```html
<div class="logo-section horizontal">
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo" class="logo inline">
    <h1 class="inline-title">La Casa de Todos</h1>
</div>
```

### **Option 3: Large Background Logo**

Add to `static/login.css`:

```css
.login-container {
    background-image: url('../images/logo-watermark.png');
    background-repeat: no-repeat;
    background-position: center;
    background-size: 200px;
    background-opacity: 0.1;
}
```

### **Option 4: Header Bar with Logo**

```html
<div class="header-bar">
    <img src="{{ url_for('static', filename='images/logo.png') }}" class="header-logo">
    <span class="header-text">La Casa de Todos</span>
</div>
```

## 🔄 **Logo Fallback System**

If no logo is found, the system automatically shows a house emoji (🏠) as a placeholder.

## 📝 **Quick Setup Checklist**

- [ ] 1. Create your logo (80x80px recommended)
- [ ] 2. Save as `static/images/logo.png`
- [ ] 3. Refresh the login page
- [ ] 4. Adjust size using CSS classes if needed
- [ ] 5. Test on different screen sizes

## 🎯 **Logo Customization Examples**

### **For a Football Team Logo:**
```css
.logo-section .logo {
    width: 90px;
    height: 90px;
    border: 3px solid #2c3e50;
    border-radius: 50%;
}
```

### **For a Family Crest:**
```css
.logo-section .logo {
    width: 70px;
    height: 90px;
    border-radius: 10px;
    border: 2px solid gold;
}
```

### **For a Modern Minimal Logo:**
```css
.logo-section .logo {
    width: 100px;
    height: 40px;
    border-radius: 20px;
    box-shadow: none;
}
```

## 📱 **Responsive Design**

The logo automatically adjusts for different screen sizes:
- **Desktop**: Full size (80x80px)
- **Tablet**: Slightly smaller (60x60px)
- **Mobile**: Optimized size (50x50px)

## 🚀 **Pro Tips**

1. **SVG logos** scale perfectly on all devices
2. **PNG with transparency** works best for complex logos
3. **Square logos** look most professional in the current layout
4. **Keep file size under 100KB** for fast loading

Your logo will now appear prominently at the top of the login page, giving your application a professional, branded appearance! 🎨✨
