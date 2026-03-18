const selects = document.querySelectorAll('select');

selects.forEach(select => {
    if (select.value === '') {
        select.style.color = '#888888';
    } else {
        select.style.color = '#000000';
        select.classList.add('has-value');
    }

    select.addEventListener('change', function () {
        if (this.value === '') {
            this.style.color = '#888888';
            this.classList.remove('has-value');
        } else {
            this.style.color = '#000000';
            this.classList.add('has-value');
        }
    });
});

const textarea = document.getElementById('associations');
if (textarea) {
    textarea.addEventListener('input', function () {
        if (this.value) {
            this.classList.add('has-value');
        } else {
            this.classList.remove('has-value');
        }
    });
}

document.getElementById('getPerfumeBtn').addEventListener('click', async function () {
    const button = this;

    const payload = {
        gender: document.getElementById('gender').value,
        aroma: document.getElementById('aroma').value,
        season: document.getElementById('season').value,
        associations: document.getElementById('associations').value,
        shop: document.getElementById('shop').value,
        llm: document.getElementById('llm').value
    };

    if (!payload.gender || !payload.aroma || !payload.season || !payload.shop || !payload.llm) {
        alert('Пожалуйста, заполните все обязательные поля!');
        return;
    }

    button.style.pointerEvents = 'none';
    button.style.opacity = '0.7';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.error || 'Ошибка при генерации результата');
        }

        localStorage.setItem(`perfume_result_${result.request_id}`, JSON.stringify(result.data));

        window.open(`/result/${result.request_id}`, '_blank');
    } catch (error) {
        alert(error.message || 'Произошла ошибка');
    } finally {
        button.style.pointerEvents = '';
        button.style.opacity = '';
    }
});

document.getElementById('clearBtn').addEventListener('click', function () {
    const clearBtn = this;

    clearBtn.style.transform = 'scale(0.95)';
    setTimeout(() => {
        clearBtn.style.transform = '';
    }, 200);

    const textarea = document.getElementById('associations');
    if (textarea) {
        textarea.value = '';
        textarea.classList.remove('has-value');
        textarea.style.color = '#888888';
    }

    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        select.selectedIndex = 0;
        select.style.color = '#888888';
        select.classList.remove('has-value');
    });
});