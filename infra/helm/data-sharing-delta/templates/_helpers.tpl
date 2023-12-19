{{/*
Expand the name of the chart.
*/}}
{{- define "data-sharing-delta.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "data-sharing-delta.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "data-sharing-delta.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "data-sharing-delta.labels" -}}
helm.sh/chart: {{ include "data-sharing-delta.chart" . }}
{{ include "data-sharing-delta.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "data-sharing-delta.selectorLabels" -}}
app.kubernetes.io/name: {{ include "data-sharing-delta.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "data-sharing-delta.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "data-sharing-delta.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Define Delta Sharing health checks
*/}}
{{- define "data-sharing-delta.healthCheck" }}
command:
  - /bin/sh
  - -c
  - >-
    wget --spider
    --header "Authorization: Bearer $DELTA_BEARER_TOKEN"
    http://{{ include "data-sharing-delta.fullname" . }}:{{ .Values.service.port }}/sharing/shares
{{- end}}
