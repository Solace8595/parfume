document.addEventListener('DOMContentLoaded', function () {
    const requestId = document.body.dataset.requestId;
    const raw = localStorage.getItem(`perfume_result_${requestId}`);

    if (!raw) {
        document.getElementById('nameField').value = 'Данные не найдены';
        document.getElementById('descriptionField').value = 'Не удалось загрузить результат. Вернитесь на главную страницу и повторите запрос.';
        return;
    }

    let data = {};
    try {
        data = JSON.parse(raw);
    } catch (e) {
        document.getElementById('nameField').value = 'Ошибка';
        document.getElementById('descriptionField').value = 'Не удалось прочитать данные результата.';
        return;
    }

    document.getElementById('nameField').value = data.name || '';
    document.getElementById('brandField').value = data.brand || '';
    document.getElementById('priceField').value = data.price || '';
    document.getElementById('descriptionField').value = data.description || '';

    const linkField = document.getElementById('linkField');
    if (data.link) {
        linkField.href = data.link;
        linkField.textContent = data.link;
    } else {
        linkField.removeAttribute('href');
        linkField.textContent = '';
    }

    const image = document.getElementById('imagePreview');

    if (data.image_url) {
        image.onload = function () {
            image.style.display = 'block';
        };

        image.onerror = function () {
            image.style.display = 'none';
            image.removeAttribute('src');
        };

        image.src = data.image_url;
    } else {
        image.style.display = 'none';
        image.removeAttribute('src');
    }
});