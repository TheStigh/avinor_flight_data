## Avinor Flight Data


Kopier mappen `avinor_flight_data` som er i `custom_components` mappen til samme mappe lokalt hos deg. 

Gjør det samme for .js filen i `www` til samme mappe lokalt hos deg.


> Lag en sensor:

```
- platform: avinor_flight_data
  name: "Avinor Flight Data Sensor"
```

Reboot Home Assistant


> Lag ditt custom lovelace card:
```
  - type: custom:avinor-flight-card
    <<: *card_mod_transparent
    title: Avinor Flydata
    entity: sensor.avinor_flight_data_sensor
```
