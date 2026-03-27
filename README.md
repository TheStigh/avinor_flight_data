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
    title: Avinor Flydata
    entity: sensor.avinor_flight_data_sensor
```

## Parser smoke test

Run the local parser smoke test with the included XML fixture:

```powershell
& "C:\Users\StighAarstein\AppData\Local\Programs\Python\Python312\python.exe" scripts/smoke_validate_parser.py --print-first
```

Optional filter check:

```powershell
& "C:\Users\StighAarstein\AppData\Local\Programs\Python\Python312\python.exe" scripts/smoke_validate_parser.py --search dy
```
