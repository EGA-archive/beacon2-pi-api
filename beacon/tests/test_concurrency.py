#!/usr/bin/env python3

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_URL = "http://localhost:5050/api/individuals"

# Número total de peticiones
TOTAL_REQUESTS = 30

# Número máximo de workers simultáneos
MAX_WORKERS = 30

# Timeout de cada petición
TIMEOUT = 60

# limit=0 => pedir todos los documentos
LIMIT = 0

# Directorio donde se guardarán las respuestas
OUTPUT_DIR = "beacon_test_results"

# Margen entre el inicio de una petición y la siguiente
# Las peticiones siguen siendo concurrentes.
REQUEST_START_MARGIN = 0


# ============================================================
# FILTROS
# ============================================================

FILTERS = [
    "NCIT:C16576",
    "ECO:0006017",
    "BTO:0004718",
]


# ============================================================
# PREPARACIÓN
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_filename(value):
    """
    Convierte un filtro en un nombre de fichero seguro.
    """
    return value.replace(":", "_").replace("/", "_").replace("\\", "_")


def find_all_ids(obj):
    """
    Recorre recursivamente todo el JSON y devuelve todos los valores
    encontrados en campos llamados 'id'.

    Sirve para comprobar si el filtro aparece en cualquier parte
    del documento.
    """
    ids = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "id" and isinstance(value, str):
                ids.append(value)

            ids.extend(find_all_ids(value))

    elif isinstance(obj, list):
        for item in obj:
            ids.extend(find_all_ids(item))

    return ids


def extract_documents(data):
    """
    Extrae los documentos de:

    response.resultSets[*].results
    """

    documents = []

    try:
        result_sets = (
            data
            .get("response", {})
            .get("resultSets", [])
        )

        for result_set in result_sets:
            results = result_set.get("results", [])

            if isinstance(results, list):
                documents.extend(results)

    except Exception:
        pass

    return documents


def get_received_filters(data):
    """
    Extrae el filtro que Beacon dice haber recibido:

    meta.receivedRequestSummary.filters
    """

    try:
        filters = (
            data
            .get("meta", {})
            .get("receivedRequestSummary", {})
            .get("filters", [])
        )

        if isinstance(filters, list):
            return filters

    except Exception:
        pass

    return []


def get_response_count(data):
    """
    Obtiene responseSummary.numTotalResults.
    """

    try:
        return (
            data
            .get("responseSummary", {})
            .get("numTotalResults")
        )
    except Exception:
        return None


# ============================================================
# UNA PETICIÓN
# ============================================================

def execute_request(request_number, filter_value):
    """
    Ejecuta UNA petición.

    Es importante que filter_value sea un argumento local de esta
    función. De esta forma cada thread conserva su propio filtro.
    """

    request_id = f"REQ-{request_number:03d}"

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # IMPORTANTE:
    #
    # Cada request construye sus propios parámetros.
    # No se utiliza ninguna variable global para el filtro.
    # --------------------------------------------------------

    params = {
        "filters": filter_value,
        "limit": LIMIT,
    }

    result = {
        "request_id": request_id,
        "expected_filter": filter_value,
        "url": BASE_URL,
        "params": params,
        "http_status": None,
        "elapsed_seconds": None,
        "status": None,
        "received_filters": [],
        "documents_count": 0,
        "expected_filter_found_in_documents": 0,
        "documents_missing_filter": [],
        "response_file": None,
        "error": None,
    }

    try:

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=TIMEOUT,
        )

        elapsed = time.perf_counter() - start_time

        result["http_status"] = response.status_code
        result["elapsed_seconds"] = round(elapsed, 3)

        # ----------------------------------------------------
        # ERROR HTTP
        # ----------------------------------------------------

        if response.status_code != 200:

            result["status"] = "HTTP_ERROR"

            # Guardamos también el cuerpo aunque sea un error
            try:
                data = response.json()
            except Exception:
                data = {
                    "raw_response": response.text
                }

        else:

            # ------------------------------------------------
            # PARSE JSON
            # ------------------------------------------------

            try:
                data = response.json()

            except Exception as exc:

                result["status"] = "INVALID_JSON"
                result["error"] = str(exc)

                return result

            # ------------------------------------------------
            # FILTROS QUE BEACON DICE HABER RECIBIDO
            # ------------------------------------------------

            received_filters = get_received_filters(data)

            result["received_filters"] = received_filters

            # ------------------------------------------------
            # DOCUMENTOS
            # ------------------------------------------------

            documents = extract_documents(data)

            result["documents_count"] = len(documents)

            # ------------------------------------------------
            # COMPROBAR QUE BEACON RECIBIÓ EL FILTRO CORRECTO
            # ------------------------------------------------

            received_filter_ok = (
                filter_value in received_filters
            )

            # ------------------------------------------------
            # COMPROBAR CADA DOCUMENTO
            #
            # El filtro debe aparecer en algún campo "id"
            # del documento.
            # ------------------------------------------------

            documents_missing = []
            documents_with_filter = 0

            for document in documents:

                document_id = document.get(
                    "id",
                    "<NO_ID>"
                )

                ids = find_all_ids(document)

                if filter_value in ids:
                    documents_with_filter += 1

                else:
                    documents_missing.append(
                        document_id
                    )

            result["expected_filter_found_in_documents"] = (
                documents_with_filter
            )

            result["documents_missing_filter"] = (
                documents_missing
            )

            # ------------------------------------------------
            # DETERMINAR RESULTADO
            # ------------------------------------------------

            if not received_filter_ok:

                result["status"] = (
                    "REQUEST_FILTER_MISMATCH"
                )

            elif documents_missing:

                result["status"] = (
                    "FILTER_MISSING_IN_DOCUMENT"
                )

            else:

                result["status"] = "OK"

        # ----------------------------------------------------
        # GUARDAR RESPUESTA
        #
        # El nombre usa filter_value LOCAL de esta petición.
        # No se obtiene de otra request.
        # ----------------------------------------------------

        filename = (
            f"{request_id}_"
            f"{safe_filename(filter_value)}.json"
        )

        filepath = os.path.join(
            OUTPUT_DIR,
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "test": result,
                    "response": data,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        result["response_file"] = filepath

    except requests.exceptions.Timeout:

        result["status"] = "TIMEOUT"
        result["elapsed_seconds"] = round(
            time.perf_counter() - start_time,
            3
        )
        result["error"] = (
            f"Timeout after {TIMEOUT} seconds"
        )

    except requests.exceptions.RequestException as exc:

        result["status"] = "REQUEST_ERROR"
        result["elapsed_seconds"] = round(
            time.perf_counter() - start_time,
            3
        )
        result["error"] = str(exc)

    except Exception as exc:

        result["status"] = "SCRIPT_ERROR"
        result["elapsed_seconds"] = round(
            time.perf_counter() - start_time,
            3
        )
        result["error"] = str(exc)

    return result


# ============================================================
# CREAR PETICIONES
# ============================================================

def build_requests():

    requests_to_run = []

    for i in range(1, TOTAL_REQUESTS + 1):

        # Repetimos los filtros en orden:
        #
        # REQ-001 -> NCIT:C16576
        # REQ-002 -> ECO:0006017
        # REQ-003 -> BTO:0004718
        # REQ-004 -> NCIT:C16576
        # ...

        filter_value = FILTERS[
            (i - 1) % len(FILTERS)
        ]

        requests_to_run.append(
            (i, filter_value)
        )

    return requests_to_run


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 78)
    print("BEACON - CONCURRENT RESPONSE ISOLATION TEST")
    print("=" * 78)
    print(f"URL:                  {BASE_URL}")
    print(f"Total requests:       {TOTAL_REQUESTS}")
    print(f"Concurrent:           {MAX_WORKERS}")
    print(f"limit:                {LIMIT}")
    print(
        f"Request start margin: "
        f"{REQUEST_START_MARGIN}s"
    )
    print(f"Output directory:     {OUTPUT_DIR}")
    print()

    requests_to_run = build_requests()

    all_results = []

    start_total = time.perf_counter()

    # --------------------------------------------------------
    # EJECUCIÓN CONCURRENTE
    # --------------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = []

        for index, (
            request_number,
            filter_value
        ) in enumerate(requests_to_run):

            # ------------------------------------------------
            # IMPORTANTE:
            #
            # Cada petición se somete al executor y esperamos
            # 0.5 segundos ANTES de iniciar/someter la siguiente.
            #
            # Esto significa:
            #
            # REQ-001 -> t=0.0s
            # REQ-002 -> t=0.5s
            # REQ-003 -> t=1.0s
            # REQ-004 -> t=1.5s
            #
            # Las peticiones continúan ejecutándose en paralelo.
            # ------------------------------------------------

            future = executor.submit(
                execute_request,
                request_number,
                filter_value,
            )

            futures.append(future)

            if index < len(requests_to_run) - 1:
                time.sleep(REQUEST_START_MARGIN)

        # ----------------------------------------------------
        # RECIBIR RESULTADOS A MEDIDA QUE TERMINAN
        # ----------------------------------------------------

        for future in as_completed(futures):

            result = future.result()

            all_results.append(result)

            # ------------------------------------------------
            # Mostrar inmediatamente el resultado
            # ------------------------------------------------

            request_id = result["request_id"]
            expected = result["expected_filter"]
            status = result["status"]
            http = result["http_status"]
            elapsed = result["elapsed_seconds"]

            docs = result["documents_count"]

            print(
                f"{request_id} | "
                f"{expected:<15} | "
                f"HTTP {str(http):<3} | "
                f"{status:<32} | "
                f"Docs: {docs:<3} | "
                f"{elapsed}s"
            )

            if result["documents_missing_filter"]:

                missing = ",".join(
                    result["documents_missing_filter"]
                )

                print(
                    f"           Documents failing: "
                    f"{missing}"
                )

    total_elapsed = (
        time.perf_counter() - start_total
    )

    # ========================================================
    # ORDENAR RESULTADOS
    # ========================================================

    all_results.sort(
        key=lambda x: x["request_id"]
    )

    # ========================================================
    # GUARDAR RESUMEN
    # ========================================================

    summary_file = os.path.join(
        OUTPUT_DIR,
        "summary.json"
    )

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "configuration": {
                    "url": BASE_URL,
                    "total_requests": TOTAL_REQUESTS,
                    "max_workers": MAX_WORKERS,
                    "limit": LIMIT,
                    "request_start_margin": REQUEST_START_MARGIN,
                    "filters": FILTERS,
                },
                "total_elapsed_seconds": round(
                    total_elapsed,
                    3
                ),
                "results": all_results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # RESUMEN FINAL
    # ========================================================

    ok = sum(
        1 for r in all_results
        if r["status"] == "OK"
    )

    filter_missing = sum(
        1 for r in all_results
        if r["status"]
        == "FILTER_MISSING_IN_DOCUMENT"
    )

    request_mismatch = sum(
        1 for r in all_results
        if r["status"]
        == "REQUEST_FILTER_MISMATCH"
    )

    http_errors = sum(
        1 for r in all_results
        if r["status"] == "HTTP_ERROR"
    )

    other_errors = len(all_results) - (
        ok
        + filter_missing
        + request_mismatch
        + http_errors
    )

    # ========================================================
    # DETECCIÓN ESPECÍFICA DE RESPUESTAS CRUZADAS
    # ========================================================

    cross_response_candidates = []

    for result in all_results:

        expected = result["expected_filter"]
        received = result["received_filters"]

        if received and expected not in received:

            cross_response_candidates.append(
                {
                    "request_id": result["request_id"],
                    "expected_filter": expected,
                    "received_filters": received,
                }
            )

    print()
    print("=" * 78)
    print("FINAL SUMMARY")
    print("=" * 78)

    print(f"Total requests:              {len(all_results)}")
    print(f"OK:                           {ok}")
    print(f"Filter missing in document:  {filter_missing}")
    print(f"Request filter mismatch:     {request_mismatch}")
    print(f"HTTP errors:                  {http_errors}")
    print(f"Other errors:                 {other_errors}")
    print(
        f"Cross-response candidates:   "
        f"{len(cross_response_candidates)}"
    )
    print(
        f"Total elapsed:                "
        f"{round(total_elapsed, 3)}s"
    )

    print()
    print(f"Responses saved in: {OUTPUT_DIR}/")
    print(f"Summary:            {summary_file}")

    # ========================================================
    # DETALLE DE POSIBLES RESPUESTAS CRUZADAS
    # ========================================================

    if cross_response_candidates:

        print()
        print("=" * 78)
        print("POSSIBLE CROSS-RESPONSE DETECTED")
        print("=" * 78)

        for item in cross_response_candidates:

            print(
                f"{item['request_id']} | "
                f"Expected: {item['expected_filter']} | "
                f"Received: {item['received_filters']}"
            )

    # ========================================================
    # DETALLE DE DOCUMENTOS INCORRECTOS
    # ========================================================

    failing_documents = []

    for result in all_results:

        if result["documents_missing_filter"]:

            failing_documents.append(
                result
            )

    if failing_documents:

        print()
        print("=" * 78)
        print("DOCUMENT VALIDATION FAILURES")
        print("=" * 78)

        for result in failing_documents:

            print(
                f"{result['request_id']} | "
                f"Filter: {result['expected_filter']} | "
                f"Missing from: "
                f"{','.join(result['documents_missing_filter'])}"
            )

    print()
    print("=" * 78)

    # ========================================================
    # CÓDIGO DE SALIDA
    # ========================================================

    if (
        filter_missing > 0
        or request_mismatch > 0
        or http_errors > 0
        or other_errors > 0
    ):

        print("TEST RESULT: FAIL")

        return 1

    else:

        print("TEST RESULT: PASS")

        return 0


if __name__ == "__main__":
    raise SystemExit(main())
