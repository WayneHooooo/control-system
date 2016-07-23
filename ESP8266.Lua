wifi.setmode(wifi.STATION)
wifi.sta.config("RaspiWiFi","66666666")
gpio.mode(4, gpio.OUTPUT)
srv=net.createServer(net.TCP)
srv:listen(80,function(conn)
    conn:on("receive", function(client,request)
        local buf = ""
        local _, _, method, path, vars = string.find(request, "([A-Z]+) (.+)?(.+) HTTP")
        if(method == nil)then
            _, _, method, path = string.find(request, "([A-Z]+) (.+) HTTP")
        end
        local _GET = {}
        if (vars ~= nil)then
            for k, v in string.gmatch(vars, "(%w+)=(%w+)&*") do
                _GET[k] = v
            end
        end
        buf = buf.."<h1> Hello, NodeMcu.</h1><form src=\"/\">Turn PIN1 <select name=\"pin\" onchange=\"form.submit()\">"
        local _on,_off = "",""
        if(_GET.pin == "ON")then
              _on = " selected=true"
              gpio.write(4, gpio.HIGH)
	      buf = <h1>ON</h1> 
        elseif(_GET.pin == "OFF")then
              _off = " selected=\"true\""
              gpio.write(4, gpio.LOW)
              buf = <h1>OFF</h1> 
        end
        client:send(buf)
    end)
    conn:on("sent", function (c) c:close() end)
end)
