import phonenumbers
from phonenumbers import geocoder, carrier

numero = phonenumbers.parse("+59170380101")  # Bolivia

pais = geocoder.description_for_number(numero, "es")
operador = carrier.name_for_number(numero, "es")

print("País:", pais)
print("Operador:", operador)