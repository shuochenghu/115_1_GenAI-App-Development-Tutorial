# 產生第12週12-1選讀的範例音檔（只需執行一次；結果已放在sample_data，build不會覆蓋）。
# 用Windows內建的中文（台灣）語音在本機合成，不呼叫任何API、不需要網路。
# 老師想改用自己的錄音時，直接用同名檔案（16 kHz、單聲道wav）取代即可。
# 執行：在Repo根目錄 powershell -ExecutionPolicy Bypass -File scripts/make_week12_voice_sample.ps1

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root "week12\week12_vision_revised\sample_data\question_total.wav"
$text = "這張收據的日期和總額是多少？"

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voice = $synth.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -eq "zh-TW" -and $_.Enabled } | Select-Object -First 1
    if ($null -eq $voice) { throw "找不到zh-TW語音：請在Windows設定加入中文（台灣）語音，或改用自己的錄音" }
    $synth.SelectVoice($voice.VoiceInfo.Name)
    $synth.Rate = -1
    # 16 kHz、16-bit、單聲道：語音辨識常用的格式，檔案也小
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    $synth.SetOutputToWaveFile($target, $format)
    $synth.Speak($text)
}
finally {
    $synth.Dispose()
}
Write-Output ("已產生 " + $target + "（" + $voice.VoiceInfo.Name + "）")
