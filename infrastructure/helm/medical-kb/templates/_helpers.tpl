{{- define "medical-kb.name" -}}
medical-kb
{{- end }}

{{- define "medical-kb.fullname" -}}
medical-kb
{{- end }}

{{- define "medical-kb.labels" -}}
app.kubernetes.io/name: {{ include "medical-kb.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
