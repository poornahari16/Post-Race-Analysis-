def compute_pes(row):
    try:
        avg_tire_size = (row["TireSize_Front"] + row["TireSize_Rear"]) / 2
        avg_pressure = (row["TirePressure_Front"] + row["TirePressure_Rear"]) / 2
        return (1 / (row["CoolantTemperature_C"] * row["DriverWeight_kg"] * avg_tire_size)) * (1 + avg_pressure / 30)
    except:
        return 0

def suggest_adjustments(row):
    suggestions = []

    def format_range(value, min_val, max_val, label, unit, emoji):
        if value < min_val:
            return f"{emoji} {label} is too low ({value}{unit}). Increase to {min_val}–{max_val}{unit}."
        elif value > max_val:
            return f"{emoji} {label} is too high ({value}{unit}). Reduce to {min_val}–{max_val}{unit}."
        else:
            return f"✅ {label} is optimal at {value}{unit} (within {min_val}–{max_val}{unit})."

    suggestions.append(format_range(row["CoolantTemperature_C"], 85, 95, "Coolant Temperature", "°C", "🌡️"))
    suggestions.append(format_range(row["DriverWeight_kg"], 68, 72, "Driver Weight", "kg", "⚖️"))

    front = row["TireSize_Front"]
    rear = row["TireSize_Rear"]
    if front != 305 or rear != 305:
        suggestions.append(f"🛞 Use 305 mm tire size for both front and rear (currently {front}/{rear}) for optimal PES.")
    else:
        suggestions.append("✅ Tire sizes are optimal at 305 mm (front and rear).")

    avg_pressure = (row["TirePressure_Front"] + row["TirePressure_Rear"]) / 2
    suggestions.append(format_range(avg_pressure, 21.5, 22.5, "Average Tire Pressure", " PSI", "🔧"))

    return suggestions
