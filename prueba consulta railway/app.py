from flask import Flask, request, render_template, redirect, url_for
import pyodbc
import os

app = Flask(__name__)


server = '192.168.1.101'
database = 'AdminAcidosMineralesDB'
username = 'sa'
password = 'Rsistems86$'
connection_string = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=no;"
)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        entrada = request.form.get("entrada")  # Código ingresado por el usuario
        fecha_inicio = request.form.get("fecha_inicio")  # Fecha "desde"
        fecha_fin = request.form.get("fecha_fin")  # Fecha "hasta"
        return redirect(url_for('resultados', entrada=entrada, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin))

    return render_template("index.html")

@app.route("/resultados")
def resultados():
    entrada = request.args.get("entrada")
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    rows = []
    error = None

    try:
        cnxn = pyodbc.connect(connection_string)
        cursor = cnxn.cursor()

        # Consulta SQL
        consulta_sql = """
        SELECT 
            SACOMP.Notas9 AS SOLICITANTE, 
            SACOMP.Notas10 AS EQUIPO, 
            SACOMP.TipoCom AS TIPO,
            SACOMP.NumeroD AS SOLICITUD,
            SACOMP.FechaT AS FECHA,
            SACOMP.CodProv, 
            SACOMP.NroUnico, 
            SACOMP.CodUsua, 
            CONCAT (SACOMP.Notas1, '', SACOMP.Notas2, '', SACOMP.Notas3, '', SACOMP.Notas4, '', SACOMP.Notas5) AS NOTA, 
            SAITEMCOM.CODITEM, 
            SAITEMCOM.DESCRIP1, 
            SAITEMCOM.CANTIDAD
        FROM SACOMP 
        JOIN SAITEMCOM ON SACOMP.NumeroD = SAITEMCOM.NumeroD
        WHERE SACOMP.TipoCom = 'S' 
            AND SACOMP.Notas10 LIKE ?
        """

        
        parametros = [f"%{entrada}%"]
        if fecha_inicio and fecha_fin:
            consulta_sql += " AND SACOMP.FechaT BETWEEN ? AND ?"
            parametros.extend([fecha_inicio, fecha_fin])

        cursor.execute(consulta_sql, parametros)
        rows = cursor.fetchall()

    except pyodbc.Error as ex:
        error = f"Error al conectar con la base de datos: {str(ex)}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnxn' in locals() and cnxn:
            cnxn.close()

    return render_template("resultados.html", rows=rows, entrada=entrada, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, error=error)

if __name__ =='__main__':
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))