// Arabic translations dictionary
const translations = {
    // UI Elements
    "Marketplace": "سوق السيارات",
    "Post a Listing": "أضف إعلان",
    "My Favorites": "المفضلة",
    "My Profile": "الملف الشخصي",
    "Logout": "تسجيل الخروج",
    "Login": "تسجيل الدخول",
    "Sign Up": "إنشاء حساب",
    "Car Listings": "إعلانات السيارات",
    "Filter Listings": "تصفية الإعلانات",
    "All Locations": "كل المواقع",
    "All Models": "كل الموديلات",
    "All Brands": "كل الماركات",
    "Max Mileage (km)": "أقصى مسافة (كم)",
    "Min Mileage (km)": "أدنى مسافة (كم)",
    "Max Price": "أعلى سعر",
    "Min Price": "أدنى سعر",
    "Clear": "مسح",
    "Filter": "تصفية",
    "Fuel Type": "نوع الوقود",
    "Transmission": "ناقل الحركة",
    "Condition": "الحالة",
    "Newly Listed": "إعلانات جديدة",
    "Sort by": "ترتيب حسب",
    "Year": "السنة",
    "Petrol": "بنزين",
    "Diesel": "ديزل",
    "Electric": "كهربائي",
    "Hybrid": "هجين",
    "Natural Gas": "غاز طبيعي",
    "Automatic": "أوتوماتيك",
    "Manual": "يدوي",
    "New": "جديد",
    "Used": "مستعمل",
    "Damaged": "متضرر",
    
    // Car listing details
    "Price:": "السعر:",
    "Mileage:": "المسافة المقطوعة:",
    "Transmission:": "ناقل الحركة:",
    "Fuel Type:": "نوع الوقود:",
    "Location:": "الموقع:",
    "Condition:": "الحالة:",
    "Details": "التفاصيل",
    "Posted on:": "تاريخ النشر:",
    "View Seller's Listings": "عرض إعلانات البائع",
    "Mark as Sold": "تعليم كمباع",
    "Description": "الوصف",
    "Contact Seller": "التواصل مع البائع",
    "EGP": "ج.م",
    "km": "كم",
    "Gas": "بنزين",
    "Price": "السعر",
    "Mileage": "المسافة المقطوعة",
    "Transmission": "ناقل الحركة",
    "Fuel Type": "نوع الوقود",
    "Location": "الموقع",
    "Condition": "الحالة",
    "Report Listing": "الإبلاغ عن الإعلان",
    "Add to Favorites": "إضافة إلى المفضلة",
    
    // Key car brands and models only (reduced for performance)
    "Toyota": "تويوتا",
    "Camry": "كامري",
    "Corolla": "كورولا",
    "Honda": "هوندا",
    "Civic": "سيفيك",
    "Nissan": "نيسان",
    "BMW": "بي إم دبليو",
    "Mercedes": "مرسيدس",
    "Hyundai": "هيونداي",
    "Kia": "كيا",
    "Ford": "فورد",
    "Chevrolet": "شيفروليه",
    "Jeep": "جيب",
    "Mazda": "مازدا",
    "Tesla": "تسلا",
    "BYD": "بي واي دي",
    "MG": "إم جي",
    "Lada": "لادا",
    "Geely": "جيلي",
    "Haval": "هافال",
    "Chery": "شيري",
    
    // Key locations
    "Cairo": "القاهرة",
    "Giza": "الجيزة",
    "Alexandria": "الإسكندرية",
    "Dokki": "الدقي",
    "Cairo Bazaar": "سوق القاهرة"
};

// Set a flag to prevent multiple simultaneous translation operations
let translationInProgress = false;
let processedElements = new Set();

// Initialization on document ready
$(document).ready(function() {
    // Apply RTL class (don't wait for translation)
    $('body').addClass('rtl');
    
    // Translate UI elements first (faster)
    setTimeout(translateUIElements, 100);
    
    // Translate content with delay
    setTimeout(function() {
        if (!translationInProgress) {
            translateContent();
        }
    }, 500);
    
    // Add minimal event handlers
    $('.dropdown-toggle').on('click', function() {
        setTimeout(translateDropdownItems, 50);
    });
    
    // Translate search placeholder
    $('input[placeholder]').each(function() {
        const placeholder = $(this).attr('placeholder');
        if (placeholder && translations[placeholder]) {
            $(this).attr('placeholder', translations[placeholder]);
        }
    });
});

// Translate UI elements (faster)
function translateUIElements() {
    // Navbar items, buttons
    $('.navbar-nav a, .btn, button, label').each(function() {
        const text = $(this).text().trim();
        if (text && translations[text]) {
            $(this).text(translations[text]);
        }
    });
}

// Translate dropdown items when opened
function translateDropdownItems() {
    $('.dropdown-menu li, .dropdown-item, option').each(function() {
        const text = $(this).text().trim();
        if (text && translations[text]) {
            $(this).text(translations[text]);
        }
    });
}

// Main content translation - progressive and non-blocking
function translateContent() {
    translationInProgress = true;
    
    // Only process elements not already translated
    translateElementsBatch($('h1, h2, h3, h4, h5, .card-title').filter(function() {
        return !processedElements.has(this);
    }).slice(0, 20), 0);
}

// Process elements in small batches to prevent UI freezing
function translateElementsBatch($elements, index) {
    if (index >= $elements.length) {
        translationInProgress = false;
        return;
    }
    
    const $element = $($elements[index]);
    processedElements.add($elements[index]);
    
    // Simple text replacement
    const text = $element.text().trim();
    if (text && translations[text]) {
        $element.text(translations[text]);
    }
    
    // Car title matching (only for appropriate elements)
    if ($element.hasClass('card-title') || $element.is('h1, h2, h3')) {
        // Match "Brand Model (Year)" pattern
        const match = text.match(/(\w+)\s+(\w+)\s+\((\d+)\)/);
        if (match) {
            const brand = match[1];
            const model = match[2];
            const year = match[3];
            
            if (translations[brand]) {
                let translatedTitle = translations[brand];
                
                if (translations[model]) {
                    translatedTitle += ` ${translations[model]}`;
                } else {
                    translatedTitle += ` ${model}`;
                }
                
                translatedTitle += ` (${year})`;
                $element.text(translatedTitle);
            }
        }
    }
    
    // Process next element with a short delay
    setTimeout(function() {
        translateElementsBatch($elements, index + 1);
    }, 0);
} 