# Pruebas de integración (U0)

Se ejecutan **tú, después de desplegar**, contra tu cuenta AWS y GitHub. Costo: prácticamente cero. Efectos: escriben y borran un registro en la tabla y un objeto en `tmp/` del bucket; **no escriben nada en GitHub**.

## Antes de empezar

```bash
export AWS_PROFILE=documentador
# Mientras main no exista, apunta la lectura de GitHub a esta rama:
export DOCUMENTADOR_GITHUB_RAMA=claude/peaceful-einstein-qc6q6f
```

## 1. Verificación rápida

```bash
uv run doc estado verificar
```
Resultado esperado: cinco líneas con ✓ (perfil, parámetros, tabla, bucket, GitHub).

## 2. Pruebas automáticas

```bash
uv run pytest -m integration tests/integration
```
Resultado esperado: 7 pruebas pasan — parámetros completos, token como SecureString, tabla y bucket de ida y vuelta, bucket privado, perfil leído desde GitHub, presupuesto de USD 10.

## 3. Prueba con la plantilla corporativa (F4)

```bash
uv run doc publicar --ejemplo --plantilla /ruta/a/corporativa.docx --salida salida/
```
Abre `salida/EST-INF-AWS-001.docx` y `.pdf` y revisa: estilos corporativos en títulos, tablas y listas; portada, encabezado y pie; marca **BORRADOR** en diagonal; enlaces en las referencias. Si se ve bien, copia la plantilla a `contenido/marco/plantilla-word/corporativa.docx`.

## Qué me envías

La salida de los pasos 1 y 2 (o el error) y tu opinión del Word/PDF del paso 3. Con eso completo el informe y cerramos la puerta de salida de U0.
