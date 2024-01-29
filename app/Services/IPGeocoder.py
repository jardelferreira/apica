import geocoder

class IPGeocoder:
    def __init__(self):
        # Sem necessidade de inicializar um objeto específico com a biblioteca geocoder
        pass

    def geolocation(ip_address):
        try:
            # Usar a função geocode do geocoder para obter informações de localização com base no endereço IP
            location = geocoder.ip(ip_address)

            # Retornar o endereço completo
            if (location.address):
                location_response = {
                    "by": "IP",
                    "success":True,
                    "lat": location.latlng[0],
                    "lng": location.latlng[1],
                    "city": location.city,
                    "state": location.state,
                    "country": location.country,
                    "address": location.address,
                    "postal": location.postal,
                    "full": f"Coordenadas geográficas: {location.latlng}, Cidade: {location.city}, Estado: {location.state}, País: {location.country}, CEP: {location.postal}"
                }
                return location_response
            else:
                return {"success":False, "message":"Endereço vinculado ao IP não encontrado."}
        except Exception as e:
            # Tratar erros, se necessário
            return {"success": False,"message": f"Erro ao obter o endereço: {str(e)}"}