from geopy.geocoders import Nominatim

class CoodinatesGeocoder:
    def __init__(self):
        # Sem necessidade de inicializar um objeto específico com a biblioteca geocoder
        pass

    def geolocation(lat: str,lng: str):
        try:
            geoLoc = Nominatim(user_agent="GetLoc")
            locname = geoLoc.reverse(f"{lat},{lng}")
            
            if(locname):
                return {
                    "success":True, "by":"latlng","full":f"{locname}"
                }
            else:
                return {"success":False, "message":"Endereço vinculado ao IP não encontrado."}
        except Exception as e:
            # Tratar erros, se necessário
            return {"success": False,"message": f"Erro ao obter o endereço: {str(e)}"}
