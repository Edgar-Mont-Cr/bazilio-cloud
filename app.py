import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from antlr4 import FileStream

from bazilio import parsear, Interprete, generar_salida, ErrorBazilio

app = Flask(__name__, static_folder='Fronted', static_url_path='')
CORS(app)

PROGRAMAS_DIR = os.path.join(os.path.dirname(__file__), 'programas')
os.makedirs(PROGRAMAS_DIR, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('Fronted', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('Fronted', filename)

@app.route('/programas/<path:filename>')
def serve_programa_file(filename):
    return send_from_directory(PROGRAMAS_DIR, filename)

@app.route('/api/compilar-generar', methods=['POST'])
def compilar_y_generar():
    data = request.json or {}
    codigo = data.get('codigo', '')
    nombre_archivo = data.get('nombre', 'programa.bzl')
    
    if not nombre_archivo.endswith('.bzl'):
        nombre_archivo += '.bzl'
        
    ruta_bzl = os.path.join(PROGRAMAS_DIR, nombre_archivo)
    
    # Preprocesador inteligente: Si el usuario escribe notas directas, las envuelve en Bazilio automáticamente
    codigo_limpio = codigo.strip()
    if "Main" not in codigo_limpio and "|:" not in codigo_limpio:
        lineas = codigo_limpio.split('\n')
        cuerpo_bazilio = []
        for l in lineas:
            notas_linea = l.strip()
            if notas_linea:
                if " " in notas_linea:
                    cuerpo_bazilio.append(f"    (:) {{{notas_linea}}}")
                else:
                    cuerpo_bazilio.append(f"    (:) {notas_linea}")
        codigo_procesado = "Main |:\n" + "\n".join(cuerpo_bazilio) + "\n:|"
    else:
        codigo_procesado = codigo

    with open(ruta_bzl, 'w', encoding='utf-8') as f:
        f.write(codigo_procesado)
        
    base_nombre = os.path.splitext(ruta_bzl)[0]
    
    try:
        arbol = parsear(FileStream(ruta_bzl, encoding="utf-8"))
        interprete = Interprete()
        interprete.cargar(arbol)
        interprete.ejecutar("Main")
        
        archivos_generados = []
        if interprete.partitura:
            generados = generar_salida(interprete.partitura, base_nombre, solo_ly=False)
            archivos_generados = [os.path.basename(a) for a in generados]
            
        return jsonify({
            'exito': True,
            'archivos': archivos_generados,
            'pdf': f"/programas/{nombre_archivo.replace('.bzl', '.pdf')}",
            'mp3': f"/programas/{nombre_archivo.replace('.bzl', '.mp3')}",
            'midi': f"/programas/{nombre_archivo.replace('.bzl', '.midi')}"
        })
    except ErrorBazilio as e:
        return jsonify({'exito': False, 'error': "Error en la compilación. Verifica que las notas existan en el piano."}), 400
    except Exception as e:
        return jsonify({'exito': False, 'error': "Error en la compilación. Verifica que las notas existan en el piano."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)