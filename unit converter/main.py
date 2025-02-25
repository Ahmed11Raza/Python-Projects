import sys

class UnitConverter:
    def __init__(self):
        # Define conversion factors for different unit types
        self.length_conversions = {
            'meters': {'meters': 1, 'kilometers': 0.001, 'centimeters': 100, 'millimeters': 1000, 'miles': 0.000621371, 'yards': 1.09361, 'feet': 3.28084, 'inches': 39.3701},
            'kilometers': {'meters': 1000, 'kilometers': 1, 'centimeters': 100000, 'millimeters': 1000000, 'miles': 0.621371, 'yards': 1093.61, 'feet': 3280.84, 'inches': 39370.1},
            'centimeters': {'meters': 0.01, 'kilometers': 0.00001, 'centimeters': 1, 'millimeters': 10, 'miles': 0.00000621371, 'yards': 0.0109361, 'feet': 0.0328084, 'inches': 0.393701},
            'millimeters': {'meters': 0.001, 'kilometers': 0.000001, 'centimeters': 0.1, 'millimeters': 1, 'miles': 0.000000621371, 'yards': 0.00109361, 'feet': 0.00328084, 'inches': 0.0393701},
            'miles': {'meters': 1609.34, 'kilometers': 1.60934, 'centimeters': 160934, 'millimeters': 1609340, 'miles': 1, 'yards': 1760, 'feet': 5280, 'inches': 63360},
            'yards': {'meters': 0.9144, 'kilometers': 0.0009144, 'centimeters': 91.44, 'millimeters': 914.4, 'miles': 0.000568182, 'yards': 1, 'feet': 3, 'inches': 36},
            'feet': {'meters': 0.3048, 'kilometers': 0.0003048, 'centimeters': 30.48, 'millimeters': 304.8, 'miles': 0.000189394, 'yards': 0.333333, 'feet': 1, 'inches': 12},
            'inches': {'meters': 0.0254, 'kilometers': 0.0000254, 'centimeters': 2.54, 'millimeters': 25.4, 'miles': 0.0000157828, 'yards': 0.0277778, 'feet': 0.0833333, 'inches': 1}
        }
        
        self.weight_conversions = {
            'kilograms': {'kilograms': 1, 'grams': 1000, 'milligrams': 1000000, 'metric_tons': 0.001, 'pounds': 2.20462, 'ounces': 35.274, 'stone': 0.157473},
            'grams': {'kilograms': 0.001, 'grams': 1, 'milligrams': 1000, 'metric_tons': 0.000001, 'pounds': 0.00220462, 'ounces': 0.035274, 'stone': 0.000157473},
            'milligrams': {'kilograms': 0.000001, 'grams': 0.001, 'milligrams': 1, 'metric_tons': 0.000000001, 'pounds': 0.00000220462, 'ounces': 0.000035274, 'stone': 0.000000157473},
            'metric_tons': {'kilograms': 1000, 'grams': 1000000, 'milligrams': 1000000000, 'metric_tons': 1, 'pounds': 2204.62, 'ounces': 35274, 'stone': 157.473},
            'pounds': {'kilograms': 0.453592, 'grams': 453.592, 'milligrams': 453592, 'metric_tons': 0.000453592, 'pounds': 1, 'ounces': 16, 'stone': 0.0714286},
            'ounces': {'kilograms': 0.0283495, 'grams': 28.3495, 'milligrams': 28349.5, 'metric_tons': 0.0000283495, 'pounds': 0.0625, 'ounces': 1, 'stone': 0.00446429},
            'stone': {'kilograms': 6.35029, 'grams': 6350.29, 'milligrams': 6350290, 'metric_tons': 0.00635029, 'pounds': 14, 'ounces': 224, 'stone': 1}
        }
        
        self.temperature_conversions = {
            'celsius': {'celsius': lambda x: x, 'fahrenheit': lambda x: (x * 9/5) + 32, 'kelvin': lambda x: x + 273.15},
            'fahrenheit': {'celsius': lambda x: (x - 32) * 5/9, 'fahrenheit': lambda x: x, 'kelvin': lambda x: ((x - 32) * 5/9) + 273.15},
            'kelvin': {'celsius': lambda x: x - 273.15, 'fahrenheit': lambda x: ((x - 273.15) * 9/5) + 32, 'kelvin': lambda x: x}
        }

        self.volume_conversions = {
            'liters': {'liters': 1, 'milliliters': 1000, 'cubic_meters': 0.001, 'gallons': 0.264172, 'quarts': 1.05669, 'pints': 2.11338, 'cups': 4.22675, 'fluid_ounces': 33.814, 'tablespoons': 67.628, 'teaspoons': 202.884},
            'milliliters': {'liters': 0.001, 'milliliters': 1, 'cubic_meters': 0.000001, 'gallons': 0.000264172, 'quarts': 0.00105669, 'pints': 0.00211338, 'cups': 0.00422675, 'fluid_ounces': 0.033814, 'tablespoons': 0.067628, 'teaspoons': 0.202884},
            'cubic_meters': {'liters': 1000, 'milliliters': 1000000, 'cubic_meters': 1, 'gallons': 264.172, 'quarts': 1056.69, 'pints': 2113.38, 'cups': 4226.75, 'fluid_ounces': 33814, 'tablespoons': 67628, 'teaspoons': 202884},
            'gallons': {'liters': 3.78541, 'milliliters': 3785.41, 'cubic_meters': 0.00378541, 'gallons': 1, 'quarts': 4, 'pints': 8, 'cups': 16, 'fluid_ounces': 128, 'tablespoons': 256, 'teaspoons': 768},
            'quarts': {'liters': 0.946353, 'milliliters': 946.353, 'cubic_meters': 0.000946353, 'gallons': 0.25, 'quarts': 1, 'pints': 2, 'cups': 4, 'fluid_ounces': 32, 'tablespoons': 64, 'teaspoons': 192},
            'pints': {'liters': 0.473176, 'milliliters': 473.176, 'cubic_meters': 0.000473176, 'gallons': 0.125, 'quarts': 0.5, 'pints': 1, 'cups': 2, 'fluid_ounces': 16, 'tablespoons': 32, 'teaspoons': 96},
            'cups': {'liters': 0.236588, 'milliliters': 236.588, 'cubic_meters': 0.000236588, 'gallons': 0.0625, 'quarts': 0.25, 'pints': 0.5, 'cups': 1, 'fluid_ounces': 8, 'tablespoons': 16, 'teaspoons': 48},
            'fluid_ounces': {'liters': 0.0295735, 'milliliters': 29.5735, 'cubic_meters': 0.0000295735, 'gallons': 0.0078125, 'quarts': 0.03125, 'pints': 0.0625, 'cups': 0.125, 'fluid_ounces': 1, 'tablespoons': 2, 'teaspoons': 6},
            'tablespoons': {'liters': 0.0147868, 'milliliters': 14.7868, 'cubic_meters': 0.0000147868, 'gallons': 0.00390625, 'quarts': 0.015625, 'pints': 0.03125, 'cups': 0.0625, 'fluid_ounces': 0.5, 'tablespoons': 1, 'teaspoons': 3},
            'teaspoons': {'liters': 0.00492892, 'milliliters': 4.92892, 'cubic_meters': 0.00000492892, 'gallons': 0.00130208, 'quarts': 0.00520833, 'pints': 0.0104167, 'cups': 0.0208333, 'fluid_ounces': 0.166667, 'tablespoons': 0.333333, 'teaspoons': 1}
        }

        # Map unit categories to their conversion dictionaries
        self.categories = {
            'length': self.length_conversions,
            'weight': self.weight_conversions,
            'temperature': self.temperature_conversions,
            'volume': self.volume_conversions
        }

    def convert(self, value, from_unit, to_unit, category):
        """Convert a value from one unit to another."""
        try:
            value = float(value)
            conversions = self.categories.get(category)
            
            if not conversions:
                return f"Error: Category '{category}' not supported."
                
            if from_unit not in conversions:
                return f"Error: Unit '{from_unit}' not found in category '{category}'."
                
            if to_unit not in conversions[from_unit]:
                return f"Error: Cannot convert from '{from_unit}' to '{to_unit}'."
                
            # Handle temperature conversions differently as they use functions
            if category == "temperature":
                result = conversions[from_unit][to_unit](value)
            else:
                result = value * conversions[from_unit][to_unit]
                
            return result
        except ValueError:
            return "Error: Please enter a valid numeric value."
        except Exception as e:
            return f"Error: {str(e)}"

    def list_units(self, category):
        """List all available units in a category."""
        if category in self.categories:
            return list(self.categories[category].keys())
        return []

    def list_categories(self):
        """List all available conversion categories."""
        return list(self.categories.keys())
        
def main():
    converter = UnitConverter()
    
    print("=== Intermediate Unit Converter ===")
    
    while True:
        print("\nAvailable categories:")
        for i, category in enumerate(converter.list_categories(), 1):
            print(f"{i}. {category.capitalize()}")
        
        try:
            category_choice = input("\nSelect a category (number or name) or 'q' to quit: ")
            
            if category_choice.lower() == 'q':
                print("Thank you for using the Unit Converter. Goodbye!")
                sys.exit(0)
                
            # Handle numeric or text input for category
            try:
                category_index = int(category_choice) - 1
                if 0 <= category_index < len(converter.list_categories()):
                    category = converter.list_categories()[category_index]
                else:
                    print("Invalid category number. Please try again.")
                    continue
            except ValueError:
                category = category_choice.lower()
                if category not in converter.list_categories():
                    print(f"Category '{category}' not found. Please try again.")
                    continue
            
            print(f"\nAvailable units for {category}:")
            units = converter.list_units(category)
            for i, unit in enumerate(units, 1):
                print(f"{i}. {unit.replace('_', ' ').capitalize()}")
            
            # Get from_unit
            from_unit_choice = input("\nConvert from (number or name): ")
            try:
                from_index = int(from_unit_choice) - 1
                if 0 <= from_index < len(units):
                    from_unit = units[from_index]
                else:
                    print("Invalid unit number. Please try again.")
                    continue
            except ValueError:
                from_unit = from_unit_choice.lower().replace(" ", "_")
                if from_unit not in units:
                    print(f"Unit '{from_unit}' not found. Please try again.")
                    continue
            
            # Get to_unit
            to_unit_choice = input("Convert to (number or name): ")
            try:
                to_index = int(to_unit_choice) - 1
                if 0 <= to_index < len(units):
                    to_unit = units[to_index]
                else:
                    print("Invalid unit number. Please try again.")
                    continue
            except ValueError:
                to_unit = to_unit_choice.lower().replace(" ", "_")
                if to_unit not in units:
                    print(f"Unit '{to_unit}' not found. Please try again.")
                    continue
            
            # Get value
            value_input = input("Enter value to convert: ")
            
            # Perform conversion
            result = converter.convert(value_input, from_unit, to_unit, category)
            
            if isinstance(result, str) and result.startswith("Error"):
                print(result)
            else:
                # Format the result based on the size of the number
                if abs(result) < 0.001 or abs(result) >= 1000000:
                    formatted_result = f"{result:.6e}"
                else:
                    formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')
                
                from_unit_display = from_unit.replace('_', ' ')
                to_unit_display = to_unit.replace('_', ' ')
                
                print(f"\n{value_input} {from_unit_display} = {formatted_result} {to_unit_display}")
                
        except KeyboardInterrupt:
            print("\nOperation canceled by user.")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
if __name__ == "__main__":
    main()