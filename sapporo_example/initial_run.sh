curl -X POST \
     -F 'workflow_params={"fastq_1":{"location":"ERR034597_1.small.fq.gz","class":"File"},"fastq_2":{"location":"ERR034597_2.small.fq.gz","class":"File"},"nthreads":2}' \
     -F 'workflow_type=CWL' \
     -F 'workflow_type_version=v1.0' \
     -F 'workflow_url=https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/trimming_and_qc.cwl' \
     -F 'workflow_engine_name=cwltool' \
     -F 'workflow_attachment=[{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_2.small.fq.gz","file_name": "ERR034597_2.small.fq.gz"},{"file_url": "https://raw.githubusercontent.com/sapporo-wes/sapporo-service/main/tests/resources/cwltool/ERR034597_1.small.fq.gz","file_name": "ERR034597_1.small.fq.gz"}]' \
     http://localhost:1122/runs
