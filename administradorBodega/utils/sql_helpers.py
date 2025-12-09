# administradorBodega/utils/sql_helpers.py
from django.db import connection

def actualizar_stock_sql(tipo_articulo, id_articulo, cantidad, operacion='SUMAR'):
    """
    Actualiza stock usando SQL directo.
    operacion: 'SUMAR' o 'RESTAR'
    """
    print(f"\n=== DEBUG SQL_HELPERS ===")
    print(f"Parámetros recibidos: tipo={tipo_articulo}, id={id_articulo}, cantidad={cantidad}, operacion={operacion}")
    
    try:
        # Mapear tipo de artículo a tabla
        tabla_map = {
            'papeleria': ('articulos_papeleria', 'id_papeleria'),
            'hardware': ('articulos_hardware', 'id_hardware'),
            'deportivo': ('articulos_deportivos', 'id_deportivo')  # Asegúrate que es 'deportivo' no 'deportivos'
        }
        
        if tipo_articulo not in tabla_map:
            print(f"❌ ERROR: Tipo de artículo '{tipo_articulo}' no está en mapa: {list(tabla_map.keys())}")
            return False
        
        tabla, id_col = tabla_map[tipo_articulo]
        print(f"DEBUG: Tabla: {tabla}, Columna ID: {id_col}")
        
        with connection.cursor() as cursor:
            # 1. Verificar que el artículo existe
            sql_check = f"SELECT cantidad_total, estado FROM {tabla} WHERE {id_col} = %s"
            print(f"DEBUG SQL: {sql_check} con parámetro {id_articulo}")
            cursor.execute(sql_check, [id_articulo])
            row = cursor.fetchone()
            
            if not row:
                print(f"❌ ERROR: Artículo {tipo_articulo} ID {id_articulo} NO encontrado en tabla {tabla}")
                return False
            
            cantidad_actual, estado_actual = row[0], row[1]
            print(f"DEBUG: Stock actual: {cantidad_actual}, Estado actual: {estado_actual}")
            
            # 2. Actualizar cantidad
            if operacion == 'SUMAR':
                sql_update = f"UPDATE {tabla} SET cantidad_total = cantidad_total + %s WHERE {id_col} = %s"
                nueva_cantidad = cantidad_actual + cantidad
            elif operacion == 'RESTAR':
                if cantidad_actual < cantidad:
                    print(f"❌ ERROR: Stock insuficiente. Actual: {cantidad_actual}, Necesita: {cantidad}")
                    return False
                sql_update = f"UPDATE {tabla} SET cantidad_total = cantidad_total - %s WHERE {id_col} = %s"
                nueva_cantidad = cantidad_actual - cantidad
            else:
                print(f"❌ ERROR: Operación '{operacion}' no válida")
                return False
            
            print(f"DEBUG SQL: {sql_update} con parámetros [{cantidad}, {id_articulo}]")
            cursor.execute(sql_update, [cantidad, id_articulo])
            
            filas_afectadas = cursor.rowcount
            print(f"DEBUG: Filas afectadas: {filas_afectadas}")
            
            if filas_afectadas == 0:
                print(f"❌ ERROR: No se pudo actualizar el artículo {tipo_articulo} ID {id_articulo}")
                return False
            
            # 3. Actualizar estado basado en la nueva cantidad
            if nueva_cantidad <= 0:
                sql_estado = f"UPDATE {tabla} SET estado = 'NO DISPONIBLE' WHERE {id_col} = %s"
                print(f"DEBUG SQL estado: {sql_estado}")
                cursor.execute(sql_estado, [id_articulo])
                print(f"✅ Estado cambiado a NO DISPONIBLE (stock: {nueva_cantidad})")
            elif operacion == 'SUMAR' and cantidad_actual <= 0 and nueva_cantidad > 0:
                # Solo cambiar a DISPONIBLE si antes estaba en 0 o NO DISPONIBLE
                sql_estado = f"UPDATE {tabla} SET estado = 'DISPONIBLE' WHERE {id_col} = %s"
                print(f"DEBUG SQL estado: {sql_estado}")
                cursor.execute(sql_estado, [id_articulo])
                print(f"✅ Estado cambiado a DISPONIBLE (stock: {nueva_cantidad})")
            else:
                print(f"ℹ️ Estado no cambiado (stock: {nueva_cantidad}, antes: {cantidad_actual})")
            
            print(f"✅ EXITO: {operacion} {cantidad} a {tipo_articulo} ID {id_articulo}")
            print(f"✅ Stock actual: {nueva_cantidad}")
            return True
            
    except Exception as e:
        print(f"❌ ERROR SQL en actualizar_stock: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False