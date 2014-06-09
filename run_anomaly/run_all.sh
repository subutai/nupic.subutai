python run_anomaly.py --inputFile data/art_load_balancer_spikes.csv --outputFile anomaly_scores_load_balancer_spikes.csv --max 4
python run_anomaly.py --inputFile data/rds_connections.csv --outputFile anomaly_scores_rds_connections.csv --max 600
python run_anomaly.py --inputFile data/cpu_cc0c5.csv --outputFile anomaly_scores_cpu_cc0c5.csv
python run_anomaly.py --inputFile data/cpu_825cc.csv --outputFile anomaly_scores_cpu_825cc.csv
python run_anomaly.py --inputFile data/cpu_5f553.csv --outputFile anomaly_scores_cpu_5f553.csv
python run_anomaly.py --inputFile data/machine_temperature.csv --outputFile anomaly_scores_machine_temperature.csv --min 0 --max 110
python run_anomaly.py --inputFile data/ambient_temperature.csv --outputFile anomaly_scores_ambient_temperature.csv --min 50 --max 100
