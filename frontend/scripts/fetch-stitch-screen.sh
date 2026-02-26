#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-10685311712153327451}"
SCREEN_ID="${2:-272e37c4893c43be986b667eb243f046}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="${ROOT_DIR}/stitch/raw"
PUBLIC_DIR="${ROOT_DIR}/public/stitch"

mkdir -p "${RAW_DIR}" "${PUBLIC_DIR}"

CODE_RESPONSE="${RAW_DIR}/screen-code-response.json"
IMAGE_RESPONSE="${RAW_DIR}/screen-image-response.json"
CODE_HTML="${RAW_DIR}/telehealth-landing-ru.html"
PUBLIC_HTML="${PUBLIC_DIR}/telehealth-landing-ru.html"
IMAGE_FILE="${PUBLIC_DIR}/telehealth-landing-ru.png"
URLS_FILE="${RAW_DIR}/hosted-urls.txt"

extract_hosted_url() {
  local source_file="$1"
  jq -r '.. | strings | select(test("^https?://"))' "${source_file}" \
    | grep -Eiv 'accounts\.google\.com|developers\.google\.com|cloud\.google\.com' \
    | head -n 1
}

run_stitch_tool() {
  local tool_name="$1"
  local output_file="$2"
  local payload="{\"projectId\":\"${PROJECT_ID}\",\"screenId\":\"${SCREEN_ID}\"}"

  if [[ -n "${STITCH_API_KEY:-}" ]]; then
    STITCH_API_KEY="${STITCH_API_KEY}" npx @_davideast/stitch-mcp tool "${tool_name}" -o json -d "${payload}" > "${output_file}"
  else
    STITCH_USE_SYSTEM_GCLOUD=1 npx @_davideast/stitch-mcp tool "${tool_name}" -o json -d "${payload}" > "${output_file}"
  fi
}

echo "1/4 Fetching Stitch screen code payload..."
if ! run_stitch_tool "get_screen_code" "${CODE_RESPONSE}"; then
  echo "Failed to fetch screen code payload."
  echo "Tip 1: set STITCH_API_KEY for key-based auth."
  echo "Tip 2: for ADC auth, set quota project:"
  echo "       gcloud auth application-default set-quota-project <GCP_PROJECT_ID>"
  exit 1
fi

echo "2/4 Fetching Stitch screen image payload..."
if ! run_stitch_tool "get_screen_image" "${IMAGE_RESPONSE}"; then
  echo "Failed to fetch screen image payload."
  echo "Tip 1: set STITCH_API_KEY for key-based auth."
  echo "Tip 2: for ADC auth, set quota project:"
  echo "       gcloud auth application-default set-quota-project <GCP_PROJECT_ID>"
  exit 1
fi

CODE_URL="$(jq -r '.htmlCode.downloadUrl // empty' "${CODE_RESPONSE}")"
IMAGE_URL="$(jq -r '.screenshot.downloadUrl // empty' "${IMAGE_RESPONSE}")"

if [[ -z "${CODE_URL}" ]]; then
  CODE_URL="$(extract_hosted_url "${CODE_RESPONSE}" || true)"
fi

if [[ -z "${IMAGE_URL}" ]]; then
  IMAGE_URL="$(extract_hosted_url "${IMAGE_RESPONSE}" || true)"
fi

if [[ -z "${CODE_URL}" ]]; then
  echo "No hosted URL found in ${CODE_RESPONSE}"
  exit 1
fi

if [[ -z "${IMAGE_URL}" ]]; then
  echo "No hosted URL found in ${IMAGE_RESPONSE}"
  exit 1
fi

echo "3/4 Downloading HTML via curl -L..."
curl -L --retry 6 --retry-all-errors --retry-delay 2 --retry-max-time 120 "${CODE_URL}" -o "${CODE_HTML}" || true
if [[ ! -s "${CODE_HTML}" ]]; then
  jq -r '.htmlContent // empty' "${CODE_RESPONSE}" > "${CODE_HTML}"
fi
cp "${CODE_HTML}" "${PUBLIC_HTML}"

echo "4/4 Downloading screenshot via curl -L..."
curl -L --retry 6 --retry-all-errors --retry-delay 2 --retry-max-time 120 "${IMAGE_URL}" -o "${IMAGE_FILE}" || true
if [[ ! -s "${IMAGE_FILE}" ]]; then
  jq -r '.screenshotBase64 // empty' "${IMAGE_RESPONSE}" | base64 --decode > "${IMAGE_FILE}"
fi

{
  echo "code_url=${CODE_URL}"
  echo "image_url=${IMAGE_URL}"
} > "${URLS_FILE}"

echo "Done."
echo "HTML:  ${CODE_HTML}"
echo "Public HTML: ${PUBLIC_HTML}"
echo "Image: ${IMAGE_FILE}"
echo "URLs:  ${URLS_FILE}"
