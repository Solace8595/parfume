// Слой 7-12: Автоматическое управление цветом текста в select
const selects = document.querySelectorAll('select');
selects.forEach(select => {
    // При загрузке
    if (select.value === '') {
        select.style.color = '#888888';
    } else {
        select.style.color = '#000000';
        select.classList.add('has-value');
    }
    
    select.addEventListener('change', function() {
        if (this.value === '') {
            this.style.color = '#888888';
            this.classList.remove('has-value');
        } else {
            this.style.color = '#000000';
            this.classList.add('has-value');
        }
    });
});

// Слой 10: Управление цветом текста в textarea
const textarea = document.getElementById('associations');
textarea.addEventListener('input', function() {
    if (this.value) {
        this.classList.add('has-value');
    } else {
        this.classList.remove('has-value');
    }
});

// Слой 15: Обработка кнопки "Получить парфюм"
document.getElementById('getPerfumeBtn').addEventListener('click', function() {
    const button = this;
    const buttonText = this.querySelector('.button-text');
    
    // Сохранение оригинального текста
    const originalText = buttonText.innerHTML;
    
    // Изменение текста
    buttonText.innerHTML = 'Ищем...';
    button.style.opacity = '0.8';
    button.style.cursor = 'wait';
    
    // Получение значений из формы
    const gender = document.getElementById('gender').value;
    const aroma = document.getElementById('aroma').value;
    const season = document.getElementById('season').value;
    const shop = document.getElementById('shop').value;
    const llm = document.getElementById('llm').value;
    const associations = document.getElementById('associations').value;
    
    // Проверка заполнения обязательных полей
    if (!gender || !aroma || !season || !shop || !llm) {
        setTimeout(() => {
            alert('Пожалуйста, заполните все обязательные поля!');
            buttonText.innerHTML = originalText;
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
        }, 500);
        return;
    }
    
    // Здесь будудт располагаться запросы к серверы
    setTimeout(() => {
        // Восстанавливаем кнопку
        buttonText.innerHTML = originalText;
        button.style.opacity = '1';
        button.style.cursor = 'pointer';
        
        // Временные данные
        const perfumes = {
            male: {
                woody: { name: "Dior Sauvage", brand: "Dior", desc: "Свежий мужской аромат" },
                fresh: { name: "Bleu de Chanel", brand: "Chanel", desc: "Элегантный парфюм" },
                floral: { name: "L'Homme", brand: "YSL", desc: "Утончённый аромат" }
            },
            female: {
                floral: { name: "Chanel N°5", brand: "Chanel", desc: "Легендарный парфюм" },
                oriental: { name: "Black Opium", brand: "YSL", desc: "Соблазнительный аромат" },
                gourmand: { name: "La Vie Est Belle", brand: "Lancôme", desc: "Сладкий парфюм" }
            },
            unisex: {
                fresh: { name: "Wood Sage & Sea Salt", brand: "Jo Malone", desc: "Свежий унисекс" },
                woody: { name: "Santal 33", brand: "Le Labo", desc: "Древесный унисекс" }
            }
        };
        
        const perfume = perfumes[gender]?.[aroma] || 
            { name: "Универсальный парфюм", brand: "Разные бренды", desc: "Подходящий под ваш запрос" };
        
        // Получение названий выбранных опций
        const shopName = document.getElementById('shop').options[document.getElementById('shop').selectedIndex].text;
        const llmName = document.getElementById('llm').options[document.getElementById('llm').selectedIndex].text;
        
        // Вывод результата
        alert(`🎯 РЕКОМЕНДОВАННЫЙ ПАРФЮМ:\n\n✨ ${perfume.name}\n🏷️ Бренд: ${perfume.brand}\n📝 Описание: ${perfume.desc}`);
    }, 1500);
});
