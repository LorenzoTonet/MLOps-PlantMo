#include <math.h>
#include <stdlib.h>

typedef struct Window {
    int Nobs;
    int cpos;
    double * vals;
};

// Variable definitions
double light_sensor_value;
double temp_sensor_value;
double air_humid_sensor_value;
double soil_humid_sensor_value;

Window * light_sensor_window;
Window * temp_sensor_window;
Window * air_humid_sensor_window;
Window * soil_humid_sensor_window;


// Function to create a new Window
Window * newWind(int Nobs)
{
    // Allocate space for the struct and the value vector
    Window * wind = (Window *) malloc(sizeof(Window));
    double * vals = (double *) malloc(sizeof(double) * Nobs);
    // Initialize the array to zero
    for (int i = 0; i < Nobs; i++)
        vals[i] = 0.0;
    // Fill the elements
    wind->Nobs = Nobs;
    wind->cpos = 0;
    wind->vals = vals;
    // Return the filled struct
    return wind;
}

// Function to add an observation to the window
void addObsWind(Window * wind, double value)
{
    int cpos = wind->cpos;
    int Nobs = wind->Nobs;

    cpos = (cpos + 1) % Nobs;
    wind->cpos = cpos;

    (wind->vals)[cpos] = value;
}

// Function to calculate the moving average
double averageWind(Window * wind)
{
    double mean = 0;
    int Nobs = wind->Nobs;
    double * vals = wind->vals;

    for (int i = 0; i < Nobs; i++)
        mean += vals[i];

    return mean / (Nobs);
}

// Calculate the standard deviation in the interval
double sdWind(Window * wind)
{
    double mean = 0;
    double sd = 0;
    double curr;
    int Nobs = wind->Nobs;
    double * vals = wind->vals;

    for (int i = 0; i < Nobs; i++)
        mean += vals[i];

    mean /= Nobs;

    for (int i = 0; i < Nobs; i++)
    {
        curr = (vals[i] - mean);
        sd += curr * curr;
    }

    sd /= Nobs;
    sd = sqrt(sd);

    return sd;
}

double maxWind(Window * wind)
{
    int Nobs = wind->Nobs;
    double * vals = wind->vals;
    double maximum = vals[0];

    for (int i = 1; i < Nobs; i++)
        maximum = max(vals[i], maximum);

    return maximum;
}

double minWind(Window * wind)
{
    int Nobs = wind->Nobs;
    double * vals = wind->vals;
    double minimum = vals[0];

    for (int i = 1; i < Nobs; i++)
        minimum = min(vals[i], minimum);

    return minimum;
}


void serialPrintWindow(Window * wind, int digits)
{
    Serial.print(averageWind(wind), digits); // Print with precision to help with debugging
    Serial.print(",");
    Serial.print(sdWind(wind), digits);
    Serial.print(",");
    Serial.print(maxWind(wind), digits);
    Serial.print(",");
    Serial.print(minWind(wind), digits);
}

void setup()
{
    pinMode(2, INPUT); // Temperatura & Humid
    pinMode(A0, INPUT); // Luce
    pinMode(A1, INPUT); // soil humid
    pinMode(A2, INPUT); // ??

    Serial.begin(115200);
    Serial.setTimeout(10);

    int wsize = 128;

    light_sensor_window      = newWind(wsize);
    temp_sensor_window       = newWind(wsize);
    air_humid_sensor_window  = newWind(wsize);
    soil_humid_sensor_window = newWind(wsize);
}

void loop()
{
    // Read a value from the sensors from the respective pins
    temp_sensor_value       = digitalRead(2);
    light_sensor_value      = analogRead(A0);
    air_humid_sensor_value  = analogRead(A1);
    soil_humid_sensor_value = analogRead(A2);

    // Add observations to the respective windows
    addObsWind(light_sensor_window, light_sensor_value);
    addObsWind(temp_sensor_window, temp_sensor_value);
    addObsWind(air_humid_sensor_window, air_humid_sensor_value);
    addObsWind(soil_humid_sensor_window, soil_humid_sensor_value);

    // Print to the serial terminal the statistics
    // In order for each of the sensors (LIGHT, TEMPERATURE, AIR HUMIDITY and SOIL HUMIDITY)
    // are collected and printed to the serial terminal separated by commas and terminated
    // by a newline character:
    //  - Sensor value in that instant
    //  - Mean over the window
    //  - Standard deviation over the window
    //  - Maximum of the Window
    //  - Minimum of the Window

    Serial.print(light_sensor_value, 8);
    Serial.print(", ");
    serialPrintWindow(light_sensor_window, 8);
    Serial.print(", ");

    Serial.print(temp_sensor_value, 8);
    Serial.print(", ");
    serialPrintWindow(temp_sensor_window, 8);
    Serial.print(", ");

    Serial.print(air_humid_sensor_value, 8);
    Serial.print(", ");
    serialPrintWindow(air_humid_sensor_window, 8);
    Serial.print(", ");

    Serial.print(soil_humid_sensor_value, 8);
    Serial.print(", ");
    serialPrintWindow(soil_humid_sensor_window, 8);

    // End of the line
    Serial.println();

    delay(15);
}
