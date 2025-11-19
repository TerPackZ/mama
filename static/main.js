// Функция, которую вызывает кнопка "←" в шапке (onclick="handleBackClick()")
window.handleBackClick = function () {
    // Если работаем внутри MAX WebApp и есть метод закрытия – используем его
    if (window.WebApp && typeof WebApp.close === "function") {
        WebApp.close();
        return;
    }

    // Обычный веб: если есть история — идём назад
    if (window.history.length > 1) {
        window.history.back();
    } else {
        // Если перейти "назад" некуда — возвращаемся на главную
        window.location.href = "/";
    }
};

document.addEventListener("DOMContentLoaded", function () {
    // MAX bridge (когда потом подключишь к MAX — это пригодится)
    if (window.WebApp && typeof WebApp.ready === "function") {
        WebApp.ready();

        if (WebApp.BackButton && typeof WebApp.BackButton.onClick === "function") {
            WebApp.BackButton.onClick(function () {
                window.handleBackClick();
            });
            WebApp.BackButton.show();
        }
    }

    // Инициализация intl-tel-input для всех полей телефона
    const phoneInputs = document.querySelectorAll('input[type="tel"]');

    phoneInputs.forEach(input => {
        if (!window.intlTelInput) return; // на всякий случай, если lib не подгрузилась

        const iti = window.intlTelInput(input, {
            initialCountry: "ru",
            preferredCountries: ["ru"],
            onlyCountries: ["ru", "by", "kz", "kg", "tj", "uz", "am", "az", "md"],
            nationalMode: false,
            autoPlaceholder: "polite",
            formatOnDisplay: true,
            utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.1.1/js/utils.js",
        });

        // Автоматическая подстановка кода страны при выборе
        input.addEventListener("countrychange", function () {
            const countryData = iti.getSelectedCountryData();
            const dialCode = countryData && countryData.dialCode ? countryData.dialCode : "7";
            input.value = "+" + dialCode + " ";
        });

        // Если поле было пустым — сразу ставим +7
        if (!input.value.trim()) {
            input.value = "+7 ";
        }
    });
});
