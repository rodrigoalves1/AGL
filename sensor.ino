#include <SPI.h>
#include "RF24.h"

/****************** User Config ***************************/
/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus pins */
RF24 radio(9,10);

byte addresses[][6] = {"1Node","2Node"};

void setup() {
    Serial.begin(115200);
    Serial.println(F("Starting..."));

    radio.begin();

    // Set the PA Level low to prevent power supply related issues since this is a
    // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
    radio.setPALevel(RF24_PA_LOW);
  
    // Open a writing and reading pipe on each radio, with opposite addresses
    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1,addresses[1]);
  
    // Start the radio listening for data
    radio.startListening();
}

void loop() {
    char buffer[5] = "hello";
    radio.printDetails();
    radio.stopListening();                                    // First, stop listening so we can talk.


    Serial.println(F("Now sending"));

    unsigned long start_time = micros();                             // Take the time, and send it.  This will block until complete
    if (!radio.write( buffer, strlen(buffer) ))
        Serial.println(F("failed"));

    // Now, continue listening
    radio.startListening();
    // Set up a timeout period, get the current microseconds
    unsigned long started_waiting_at = micros();
    // Set up a variable to indicate if a response was received or not
    boolean timeout = false;
  
  // While nothing is received
    while (!radio.available() ) {
        // If waited longer than 200ms, indicate timeout and exit while loop
        if (micros() - started_waiting_at > 200000 ){
            timeout = true;
            break;
        }      
    }

    if ( timeout ) {                                             // Describe the results
        Serial.println(F("Failed, response timed out."));
    } else {
        unsigned long got_time;                                 // Grab the response, compare, and send to debugging spew
        radio.read( &got_time, sizeof(unsigned long) );
        unsigned long end_time = micros();

        // Spew it
        Serial.print(F("Sent "));
        Serial.print(start_time);
        Serial.print(F(", Got response "));
        Serial.print(got_time);
        Serial.print(F(", Round-trip delay "));
        Serial.print(end_time-start_time);
        Serial.println(F(" microseconds"));
    }
    // Try again 1s later
    delay(1000);
}

