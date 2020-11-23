require 'json'
require 'date'

# TODO add arg parse


def main
  dates_reg = get_dates_reg

  sm_resp = JSON.load(`aws secretsmanager get-secret-value --secret-id "#{ARGV[0]}"`)
  
  if !sm_resp.include? "SecretString"
    raise Exception.new "Unable to find secret!"
  end

  secret_str = JSON.load(sm_resp['SecretString'])  
  secret_str = secret_str[ARGV[0].split("/")[-1]]

  cmd = %{
  curl -G \
      "https://app.datadoghq.com/report/hourly_data/monitor" \
      -d "api_key=#{secret_str}" \
      -d "application_key=#{ARGV[1]}" | grep "#{ARGV[2]}" | grep -E "#{dates_reg}" >> datadog_info.csv
  }
  `#{cmd}`

  `cat datadog_info.csv | cut -d$',' -f 3,3 | sort | uniq -c >> tmp_report.csv`

  File.open("tmp_report.csv").read.each_line do |l|
    # transform output from strings like 
    # "   4 "[TEST] Unhandled Exception on Conversions Job"  " to 
    # "40,attentive-prod-read1 RDS Replication Failed"
    line_split = l.split("\"")
    puts "#{line_split[0].gsub(" ","")},#{line_split[-2]}"
  end

  `rm tmp_report.csv`
  `rm datadog_info.csv`

end

def get_dates_reg
  d1 = Date.parse(ARGV[3])
  d2 = Date.parse(ARGV[4])

  dates = (d1..d2).map {|d| d.strftime("%Y-%m-%d") }.join("|")
  "(#{dates})"
end

main
