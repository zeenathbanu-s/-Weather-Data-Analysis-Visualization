const form = document.getElementById("weatherForm");
const resultDiv = document.getElementById("result");
const chartCanvas = document.getElementById("weatherChart");
const dateInput = document.getElementById("dateInput");
const modeButtons = document.querySelectorAll(".mode-btn");
const locBtn = document.getElementById("locBtn");
let selectedMode = "current";
let weatherChart = null;

modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        modeButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        selectedMode = btn.dataset.mode;
        dateInput.style.display = (selectedMode === "current") ? "none" : "block";
        if (selectedMode === "current") dateInput.value = "";
    });
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    fetchWeather(new FormData(form));
});

locBtn.addEventListener("click", () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const formData = new FormData();
            formData.append("location", `${position.coords.latitude},${position.coords.longitude}`);
            formData.append("date", dateInput.value);
            fetchWeather(formData);
        }, err => alert("Unable to get location: " + err.message));
    } else {
        alert("Geolocation not supported.");
    }
});

async function fetchWeather(formData) {
    resultDiv.querySelector("#extra-info").innerHTML = "<p><b>Loading...</b></p>";
    const response = await fetch("/get_weather", {method: "POST", body: formData});
    const data = await response.json();
    if (data.error) {
        resultDiv.querySelector("#extra-info").innerHTML = `<p class='error'>${data.error}</p>`;
        return;
    }
    updateUI(data);
}

function updateUI(data) {
    const weather = data.weather;
    let tempC = "--", feelsC = "--", humidity = "--", wind = "--", condition = "--";

    if (weather.current) {
        const c = weather.current;
        tempC = c.temp_c; feelsC = c.feelslike_c; humidity = c.humidity; wind = c.wind_kph; condition = c.condition.text;
        drawChart([tempC, feelsC, humidity, wind]);
    } else if (weather.forecast && weather.forecast.forecastday) {
        const d = weather.forecast.forecastday[0].day;
        tempC = d.avgtemp_c; feelsC = d.maxtemp_c; humidity = d.avghumidity; wind = d.maxwind_kph; condition = d.condition.text;
        drawChart([tempC, feelsC, humidity, wind]);
    }

    document.getElementById("temp").innerHTML = `🌡️ Temp: ${tempC}°C`;
    document.getElementById("feels").innerHTML = `🤔 Feels: ${feelsC}°C`;
    document.getElementById("humidity").innerHTML = `💧 Humidity: ${humidity}%`;
    document.getElementById("wind").innerHTML = `💨 Wind: ${wind} kph`;
    document.getElementById("condition").innerHTML = `☁️ ${condition}`;

    const locInfo = weather.location ? `<h3>${weather.location.name}, ${weather.location.country}</h3>
        <p><b>Local Time:</b> ${weather.location.localtime}</p>` : "";

    resultDiv.querySelector("#extra-info").innerHTML = `<h2>${data.type}</h2>${locInfo}`;
}

function drawChart(values) {
    if (weatherChart) weatherChart.destroy();
    weatherChart = new Chart(chartCanvas, {
        type: "bar",
        data: {labels: ["Temp","Feels","Humidity","Wind"], datasets:[{label:"Weather Parameters", data:values, backgroundColor:["#ffadad","#ffd6a5","#caffbf","#9bf6ff"], borderWidth:1}]},
        options:{scales:{y:{beginAtZero:true}}}
    });
}
