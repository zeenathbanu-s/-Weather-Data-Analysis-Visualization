#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <time.h>
#include <json-c/json.h>

#define API_KEY "e3b8cf522cd44439b46153354250311"
#define BASE_URL "http://api.weatherapi.com/v1"
#define MAX_CITIES 20
#define MAX_CITY_LEN 50
#define OUTPUT_FILE "all_cities_weather.csv"  // Saved in same folder

struct MemoryStruct {
    char *memory;
    size_t size;
};

size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    struct MemoryStruct *mem = (struct MemoryStruct *)userp;
    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if(ptr == NULL) return 0;
    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;
    return realsize;
}

char* fetch_weather(const char* url) {
    CURL *curl;
    CURLcode res;
    struct MemoryStruct chunk;
    chunk.memory = malloc(1);
    chunk.size = 0;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "❌ curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            free(chunk.memory);
            return NULL;
        }
    }
    curl_global_cleanup();
    return chunk.memory;
}

void save_to_csv(FILE *fp, const char* city, const char* date, double temp, int hum, double wind,
                 const char* cond, double precip, double feels, double vis,
                 double uv, double pressure, const char* type) {
    fprintf(fp, "%s,%s,%s,%.1f,%d,%.1f,%s,%.1f,%.1f,%.1f,%.1f,%.1f\n",
            city, type, date, temp, hum, wind, cond, precip, feels, vis, uv, pressure);
}

void print_weather_table(const char* city, char** json_list, int count, const char* type, FILE *fp) {
    printf("\n=== %s Weather for %s ===\n", type, city);
    printf("Date         | Temp(C) | Hum(%%) | Wind(kph) | Condition        | Precip(mm) | Feels(°C) | Vis(km) | UV | Pressure(mb)\n");
    printf("---------------------------------------------------------------------------------------------------------------\n");

    for(int i=0; i<count; i++) {
        if(!json_list[i]) continue;
        struct json_object *parsed_json = json_tokener_parse(json_list[i]);
        if(!parsed_json) continue;

        if(strcmp(type, "Current") == 0) {
            struct json_object *current=NULL, *location=NULL;
            json_object_object_get_ex(parsed_json, "current", &current);
            json_object_object_get_ex(parsed_json, "location", &location);
            if(current && location) {
                const char* date = json_object_get_string(json_object_object_get(location, "localtime"));
                double temp = json_object_get_double(json_object_object_get(current, "temp_c"));
                int hum = json_object_get_int(json_object_object_get(current, "humidity"));
                double wind = json_object_get_double(json_object_object_get(current, "wind_kph"));
                const char* cond = json_object_get_string(json_object_object_get(json_object_object_get(current, "condition"), "text"));
                double precip = json_object_get_double(json_object_object_get(current, "precip_mm"));
                double feels = json_object_get_double(json_object_object_get(current, "feelslike_c"));
                double vis = json_object_get_double(json_object_object_get(current, "vis_km"));
                double uv = json_object_get_double(json_object_object_get(current, "uv"));
                double pressure = json_object_get_double(json_object_object_get(current, "pressure_mb"));
                printf("%-13s | %-7.1f | %-6d | %-9.1f | %-15s | %-10.1f | %-8.1f | %-7.1f | %-2.1f | %-5.1f\n",
                       date, temp, hum, wind, cond, precip, feels, vis, uv, pressure);
                save_to_csv(fp, city, date, temp, hum, wind, cond, precip, feels, vis, uv, pressure, type);
            }
        } else {
            struct json_object *forecast=NULL;
            if(!json_object_object_get_ex(parsed_json,"forecast",&forecast)) {
                free(json_list[i]);
                continue;
            }
            struct json_object *forecastday = json_object_object_get(forecast,"forecastday");
            if(!forecastday || json_object_get_type(forecastday)!=json_type_array) continue;
            int len = json_object_array_length(forecastday);
            for(int j=0; j<len; j++) {
                struct json_object *day_obj = json_object_array_get_idx(forecastday,j);
                struct json_object *day_data = json_object_object_get(day_obj,"day");
                if(!day_data) continue;
                const char* date = json_object_get_string(json_object_object_get(day_obj,"date"));
                double temp = json_object_get_double(json_object_object_get(day_data,"avgtemp_c"));
                int hum = json_object_get_int(json_object_object_get(day_data,"avghumidity"));
                double wind = json_object_get_double(json_object_object_get(day_data,"maxwind_kph"));
                const char* cond = json_object_get_string(json_object_object_get(json_object_object_get(day_data, "condition"), "text"));
                double precip = json_object_get_double(json_object_object_get(day_data, "totalprecip_mm"));
                double feels = json_object_get_double(json_object_object_get(day_data, "avgtemp_c")); // approx
                double vis = json_object_get_double(json_object_object_get(day_data, "avgvis_km"));
                double uv = json_object_get_double(json_object_object_get(day_data, "uv"));
                double pressure = 1013.0; // average default
                printf("%-10s | %-7.1f | %-6d | %-9.1f | %-15s | %-10.1f | %-8.1f | %-7.1f | %-2.1f | %-5.1f\n",
                       date, temp, hum, wind, cond, precip, feels, vis, uv, pressure);
                save_to_csv(fp, city, date, temp, hum, wind, cond, precip, feels, vis, uv, pressure, type);
            }
        }
        free(json_list[i]);
    }
}

void get_dates(char dates[7][11], int past) {
    time_t t = time(NULL);
    struct tm tm_info = *localtime(&t);
    for(int i=0;i<7;i++){
        struct tm tmp = tm_info;
        if(past) tmp.tm_mday -= (7 - i);
        else tmp.tm_mday += (i + 1);
        mktime(&tmp);
        strftime(dates[i], 11, "%Y-%m-%d", &tmp);
    }
}

int main(int argc, char** argv) {
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int n_cities;
    char cities[MAX_CITIES][MAX_CITY_LEN];

    if(rank == 0) {
        printf("Enter number of cities: "); fflush(stdout);
        scanf("%d", &n_cities);
        for(int i=0; i<n_cities; i++) {
            printf("Enter city name: "); fflush(stdout);
            scanf("%s", cities[i]);
        }
    }

    MPI_Bcast(&n_cities, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(cities, MAX_CITIES * MAX_CITY_LEN, MPI_CHAR, 0, MPI_COMM_WORLD);

    // Rank 0 creates the CSV file with header
    if(rank == 0) {
        FILE *fp = fopen(OUTPUT_FILE, "w");
        if (fp == NULL) {
            printf("❌ Error creating CSV file.\n");
            MPI_Finalize();
            return 1;
        }
        fprintf(fp, "City,Type,Date,Temp(C),Humidity(%%),Wind(kph),Condition,Precip(mm),FeelsLike(°C),Visibility(km),UV,Pressure(mb)\n");
        fclose(fp);
    }
    MPI_Barrier(MPI_COMM_WORLD);

    for(int c = 0; c < n_cities; c++) {
        if(c % size == rank) {
            char city[MAX_CITY_LEN];
            strcpy(city, cities[c]);
            char url[512];

            FILE *fp = fopen(OUTPUT_FILE, "a");
            if(!fp) continue;

            // Past 7 days
            char past_dates[7][11];
            get_dates(past_dates, 1);
            char* history_json[7];
            for(int d = 0; d < 7; d++) {
                snprintf(url, 512, "%s/history.json?key=%s&q=%s&dt=%s", BASE_URL, API_KEY, city, past_dates[d]);
                history_json[d] = fetch_weather(url);
            }
            print_weather_table(city, history_json, 7, "History", fp);

            // Current
            snprintf(url, 512, "%s/current.json?key=%s&q=%s", BASE_URL, API_KEY, city);
            char* current_json = fetch_weather(url);
            char* current_list[1] = { current_json };
            print_weather_table(city, current_list, 1, "Current", fp);

            // Future 7 days
            snprintf(url, 512, "%s/forecast.json?key=%s&q=%s&days=7", BASE_URL, API_KEY, city);
            char* forecast_json = fetch_weather(url);
            char* forecast_list[1] = { forecast_json };
            print_weather_table(city, forecast_list, 1, "Forecast", fp);

            fclose(fp);
            printf("✅ Data saved for %s in %s\n", city, OUTPUT_FILE);
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }

    if(rank == 0)
        printf("\n🌦️ All city data saved successfully in '%s' (in your current folder)\n", OUTPUT_FILE);

    MPI_Finalize();
    return 0;
}

