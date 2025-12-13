# MusictoSound
TFG

# COSAS A EJECUTAR TODOS LOS DIAS
Conectarse con la api
$Env:OPENAI_API_KEY = "tu-api-key-aquí"

combrobar la conexion con la api
echo $Env:OPENAI_API_KEY

Para guardar los cambios en la memoria ejecutar en el terminal:
Add-Content "docs\diario.md" "## $(Get-Date -Format 'yyyy-MM-dd')`n"
python scripts/generate_memoria.py

# COMANDOS UTILES
Para mostrar el arbol de archivos
tree /F

Pruebas habituales con los pdf
Introduce la ruta PDF de la partitura: C:\Users\34690\Documents\1. Universidad\TFG\Coro\Ay amante mío.pdf 
Introduce la carpeta de salida para el XML (o deja vacío para usar 'output'): C:\Users\34690\Documents\1. Universidad\TFG\pruebas_salida_visual
