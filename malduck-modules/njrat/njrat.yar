rule win_njrat {
    meta:
        author = "CERT Polska"
        date = "2020-07-20"
        hash = "998b6ed5494b22e18d353fdd96226db3"
        description = "Detects unpacked NjRAT malware."
        reference = "https://malpedia.caad.fkie.fraunhofer.de/details/win.njrat"

    strings:
        $str_cmd1 = "md.exe /k ping 0 & del " wide
        $str_cmd2 = "cmd.exe /c ping 127.0.0.1 & del" wide
        $str_cmd3 = "cmd.exe /c ping" wide
        $str_cmd4 = "cmd.exe /C Y /N /D Y /T 1 & Del" wide

        $str_kl1 = "[kl]" wide
        $str_kl2 = "[TAP]" wide
        $str_kl3 = "[ENTER]" wide


        $op_config_07d = { 46 69 78 00 6B 00 57 52 4B 00 6D 61 69 6E 00 00 00 }
        $op_config_07d_indirect = { 54 00 45 00 4d 00 50 00 00 [1] 65 00 78 00 65 }

        $op_config_07nc = { 63 00 6C 00 65 00 61 00 72 00 00 }

    condition:
        1 of ($str_cmd*) and
        1 of ($str_kl*) and
        1 of ($op_config*)
}
