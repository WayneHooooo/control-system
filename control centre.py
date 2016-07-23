# -*- coding: utf-8 -*-
import socket
import sqlite3
import thread
import time
import urllib
import urllib2

def httpclient(ip,state):
    try:
        send = "http://"+ ip + "/?pin="+ state
        req = urllib2.Request(send)
        res_data = urllib2.urlopen(req)
        res =  res_data.read()
        feedback=(res.split(">")[1]).split("<")[0]
        return feedback
    except:
        return "error"

def httpclient2(ip,state):
    try:
        send = "http://"+ ip + "/?pin="+ state
        req = urllib2.Request(send)
        res_data = urllib2.urlopen(req)        
    except:
        return "error"
    
def led_system():
    thread.start_new_thread(tcpsocket,())
    thread.start_new_thread(timeschedule,())

def timer():
    t=""
    while (cmp(t,"00")):
        time.sleep(1)
        t= time.strftime("%S",time.localtime())
        print t
    print "it is 00 now"
        
        
def timeschedule():
    #database
    db=sqlite3.connect("/home/pi/LEDSystem/leddatabase.db")
    c=db.cursor()
    global schedulename,stime,etime,wd,we
    schedulename=[]
    stime=[]
    etime=[]
    wd=[]
    we=[]    
    c.execute("SELECT schedulename,stime,etime,wd,we FROM Schedule WHERE status ='1'")
    for i in c:
       schedulename.append(i[0])
       stime.append(i[1])
       etime.append(i[2])
       wd.append(i[3])
       we.append(i[4])
    while 1:
        #get system time
        t=""
        while (cmp(t,"00")):
            time.sleep(1)
            t= time.strftime("%S",time.localtime())
            print t
        print "it is 00 now"
        systime=time.strftime("%a %H:%M",time.localtime())
        date,ctime=systime.split(" ")
        if (cmp(date,"Sat") and cmp(date,"Sun")):
            print "weekdays"
            n=0
            for j in wd:
                if cmp(j,"1")==0: 
                    print "comparing "+stime[n]+" and "+ctime
                    if cmp(stime[n],ctime)==0:                    
                        c.execute("SELECT led FROM schedule"+schedulename[n])
                        print schedulename[n]
                        for k in c:
                            httpclient2(k[0],"ON")
                            print k,"ON"
                    if cmp(etime[n],ctime)==0:
                        c.execute("SELECT led FROM schedule"+schedulename[n])
                        for k in c:
                            httpclient(k[0],"OFF")
                            print k[0],"OFF"
                n+=1
        else:
            print "weekends"
            n=0
            for j in wd:
                if cmp(j,"1")==0:
                    if cmp(stime[n],ctime)==0:
                        c.execute("SELECT led FROM schedule"+schedulename[i])
                        for k in c:
                            #httpclient(k[0],"ON")
                            print k[n],"ON"
                    if cmp(etime[n],ctime)==0:
                        c.execute("SELECT led FROM schedule"+schedulename[i])
                        timer()
                        for k in c:
                            #httpclient(k[0],"OFF")
                            print k[n],"OFF"
                n+=1

def time_up():
    global Time_up,conn,state
    Time_up=300
    
    while (Time_up and (state!=0)):
        time.sleep(1)
        Time_up-=1
        
    conn.send("98>socket closed\n")
    conn.close()
    state=0
    
def countdown(ip,hour,mins):
    hour=hour*60*60
    mins=mins*60
    time.sleep(hour+mins)
    httpclient(ip,"OFF")
    
def tcpsocket():
    #database
    db=sqlite3.connect("/home/pi/LEDSystem/leddatabase.db")
    c=db.cursor()
    try:
        c.execute("CREATE TABLE settings (name TEXT PRIMARY KEY, v TEXT)")
    except:
        print "has this table already"
    else:
        c.execute("INSERT INTO settings VALUES ('account','admin')")
        c.execute("INSERT INTO settings VALUES ('psw','admin')")
        db.commit()
    c.execute("CREATE TABLE IF NOT EXISTS Room (roomname TEXT PRIMARY KEY, roomlednumber INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS Schedule (schedulename TEXT PRIMARY KEY, stime TEXT, "
              +"etime TEXT, wd TEXT, we TEXT, status TEXT)")

    '''#for testing
    c.execute("CREATE TABLE IF NOT EXISTS location_table (ledlocation TEXT PRIMARY KEY, ledip INTEGER)")
    c.execute("INSERT INTO location_table VALUES ('livingroom1','10.0.0.60')")
    c.execute("INSERT INTO location_table VALUES ('livingroom2','10.0.0.61')")
    c.execute("INSERT INTO Room VALUES ('livingroom',2)")
    c.execute("INSERT INTO Room VALUES ('bedroom',0)")
    c.execute("INSERT INTO Room VALUES ('bathroom',0)")
    c.execute("CREATE TABLE livingroom (ledname TEXT PRIMARY KEY, ledip TEXT, ledwatt TEXT,"
              +"ledstate TEXT, turnontime TEXT, totaltime TEXT)")
    c.execute("CREATE TABLE bedroom (ledname TEXT PRIMARY KEY, ledip TEXT, ledwatt TEXT,"
              +"ledstate TEXT, turnontime TEXT, totaltime TEXT)")
    c.execute("CREATE TABLE bathroom (ledname TEXT PRIMARY KEY, ledip TEXT, ledwatt TEXT,"
              +"ledstate TEXT, turnontime TEXT, totaltime TEXT)")
    c.execute("INSERT INTO livingroom (ledname,ledip,ledwatt,ledstate,totaltime) VALUES ('leftside','10.0.0.60','20','0','30')")
    c.execute("INSERT INTO livingroom (ledname,ledip,ledwatt,ledstate,totaltime) VALUES ('rightside','10.0.0.61','30','0','25')")
    db.commit()
    '''#for testing

    #initial TCP socket
    Host="192.168.1.130"
    #Host="10.0.0.1"
    Port=8877
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((Host,Port))
    s.listen(1)
    global conn,state
    while 1:
        global Time_up, schedulename,stime,etime,wd,we
        info = []
        c.execute("SELECT v FROM settings WHERE name = 'account'")#get the account and psw
        info.append(c.fetchone()[0])
        c.execute("SELECT v FROM settings WHERE name = 'psw'")  
        info.append(c.fetchone()[0])
        print "waiting for connection"
        conn,addr = s.accept()
        print "Connected by",addr
        state = 1
        msg = conn.recv(1024)
        if not msg:
            break
        else:#check the password
            print msg
            account,psw = msg.split(",")
            print account,psw
            if(cmp(account,info[0]) or cmp(psw,info[1])):
                print "wrong password"
                conn.send("0>wrong\n")
            else:
                print "correct password"
                conn.send("0>correct\n")
                thread.start_new_thread(time_up,())
                
                while(state!=0):#into receiving command loop
                    print "waiting for message"
                    msg = conn.recv(1024)
                    if not msg:
                        break
                    else:
                        Time_up=300#reset countdown timer
                        cmd,data = msg.split(",")
                        print cmd
                        if cmp(cmd,"initial")==0:#update all information
                            c.execute("SELECT roomname,roomlednumber FROM Room")
                            roomnumber=0
                            roomname=""
                            roomName=[]
                            roomlednumber=""
                            for i in c:
                                roomnumber+=1
                                roomname+=i[0]+","
                                roomName.append(i[0])
                                roomlednumber+=str(i[1])+","
                            sql="1>"+str(roomnumber)+"|no|"+roomname+"|"+roomlednumber+"|"#led details in each room has not input yet
                            ledname=""
                            ledip=""
                            ledwatt=""
                            ledstate=""
                            for i in range(roomnumber):
                                print i
                                ss=""
                                c.execute("SELECT ledname,ledip,ledwatt,ledstate FROM "+roomName[i])
                                for j in c:
                                    ss=" "
                                    ledname+=j[0]+","
                                    ledip+=j[1]+","
                                    ledwatt+=j[2]+","
                                    ledstate+=j[3]+','
                                if cmp(ss,"")==0:
                                    ledname+=","
                                    ledip+=","
                                    ledwatt+=","
                                    ledstate+=","
                                ledname+="<"
                                ledip+="<"
                                ledwatt+="<"
                                ledstate+="<"
                            sql=sql+ledname+"|"+ledip+"|"+ledwatt+"|"+ledstate+"\n"
                            print sql
                            conn.sendall(sql)
                                #conn.sendall("1>3|no|livingroom,bedroom,bathroom,|2,2,1,|led1,led2,<led3,led5,<led,|123,122,<111,222,<33,|10,10,<30,23,<33|0,0,<1,0,<1,\n")
                        elif cmp(cmd,"add room")==0:#add a new room
                            c.execute("INSERT INTO Room VALUES ('"+data+"',0)")
                            c.execute("CREATE TABLE "+data+" (ledname TEXT PRIMARY KEY, ledip TEXT, ledwatt TEXT,"
                                      +"ledstate TEXT, turnontime TEXT, totaltime TEXT)")
                            conn.send("0>confirm\n")
                            print data
                        elif cmp(cmd,"change psw")==0:#change psw
                            print data
                            opsw,npsw = data.split("<")
                            if cmp(opsw,info[1])==0:
                                if cmp(npsw,opsw)==0:
                                    conn.send("2>same\n")
                                else:
                                    c.execute("UPDATE settings SET v=? WHERE name='psw'",(npsw))
                                    db.commit()
                                    info[1]=npsw
                                    conn.send("2>confirm\n")
                            else:
                                conn.send("2>wrong\n")
                        elif cmp(cmd,"change username")==0:#change user name
                            usrname,psw = data.split("<")
                            print usrname,psw
                            if cmp(usrname,info[0])==0:
                                conn.send("3>same\n")
                            else:
                                if cmp(psw,info[1])==0:
                                    c.execute("UPDATE settings SET v=? WHERE name='account'",(usrname))
                                    db.commit()
                                    info[0]=usrname
                                    conn.send("3>confirm\n")
                                else:
                                    conn.send("3>wrong\n")                                                
                        elif cmp(cmd,"turn on all")==0:
                            c.execute("SELECT ledip FROM "+data)
                            for i in c:
                                httpclient(i[0],"ON")
                                print i[0]
                            c.execute("UPDATE "+data+" SET ledstate ='1' WHERE ledstate='0'")
                            print data
                            conn.send("5>confirm\n")
                        elif cmp(cmd,"turn off all")==0:#turn off all
                            print data
                            c.execute("SELECT ledip FROM "+data)
                            for i in c:
                                httpclient(i[0],"OFF")
                                print i[0]
                            c.execute("UPDATE "+data+" SET ledstate ='0' WHERE ledstate='1'")
                            conn.send("6>confirm\n")
                            
                        elif cmp(cmd,"change roomname")==0:#change room name
                            oname,nname=data.split("<")
                            print oname,nname
                            c.execute("UPDATE Room SET roomname='"+nname+"' WHERE roomname='"+oname+"'")
                            c.execute("ALTER TABLE "+oname+" RENAME TO "+nname)
                            db.commit()
                            conn.send("7>confirm\n")
                            print data
                        elif cmp(cmd,"delete room")==0:#delete a room
                            c.execute("DELETE FROM Room WHERE roomname ='"+data+"'")
                            c.execute("DROP TABLE "+data)
                            db.commit()
                            conn.send("8>confirm\n")
                            print data
                        elif cmp(cmd,"get location")==0:#get location and ip
                            c.execute("SELECT ledlocation,ledip FROM location_table")
                            ledlocation="Please choose led's location<"
                            ledip=" <"
                            for i in c:
                                ledlocation+=i[0]+"<"
                                ledip+=i[1]+"<"
                            feedback="4>"+ledlocation+","+ledip+"\n"
                            print feedback
                            conn.send(feedback)                                
                        elif cmp(cmd,"add led")==0:#add led
                            print data                        
                            roomname,lednumber,ledname,ledip,ledwatt=data.split(">")
                            c.execute("INSERT INTO "+roomname+" (ledname,ledip,ledwatt,ledstate,totaltime) VALUES ('"+ledname+"','"+ledip+"','"+ledwatt+"','0','0')")
                            lednumber=int(lednumber)+1
                            c.execute("UPDATE Room SET roomlednumber="+str(lednumber)+" WHERE roomname='"+roomname+"'")
                            db.commit()
                            #insert to sqlite
                            conn.send("0>confirm\n")
                        elif cmp(cmd,"turn on")==0:#turn on one
                            roomname,ip =data.split("<")
                            feedback=httpclient(ip,"ON")
                            
                            systime = time.strftime("%H:%M",time.localtime())
                            
                            if cmp(feedback,"ON")==0:
                                c.execute("UPDATE "+roomname+" SET ledstate = '1' WHERE ledip = '"+ip+"'")
                                c.execute("UPDATE "+roomname+" SET turnontime = '"+systime+"' WHERE ledip = '"+ip+"'")
                                conn.send("1>on\n")
                            else:
                                conn.send("99>error\n")
                        elif cmp(cmd,"turn off")==0:#turn off one
                            print data
                            roomname,ip=data.split("<")
                            feedback=httpclient(ip,"OFF")
                            c.execute("SELECT turnontime,totaltime FROM "+roomname+" WHERE ledip='"+ip+"'")
                            temp=c.fetchone()
                            ontime=temp[0]
                            t=temp[1]                            
                            systime=time.strftime("%H:%M",time.localtime())
                            onhour,onmin=ontime.split(":")
                            offhour,offmin=systime.split(":")
                            t=str(int(t)+(int(offhour)-int(onhour))*60+(int(offmin)-int(onmin)))
                            if cmp(feedback,"OFF")==0:
                                c.execute("UPDATE "+roomname+" SET ledstate = '0' WHERE ledip = '"+ip+"'")
                                c.execute("UPDATE "+roomname+" SET totaltime = '"+t+"' WHERE ledip = '"+ip+"'")
                                conn.send("1>off\n")
                            else:
                                conn.send("99>error\n")
                                
                        elif cmp(cmd,"edit led")==0:#edit a led
                            print data
                            roomname,oldname,ledname,ledip,ledwatt=data.split(">")
                            c.execute("UPDATE "+roomname+" SET ledip = '"+ledip+"' WHERE ledname = '"+oldname+"'")
                            c.execute("UPDATE "+roomname+" SET ledwatt = '"+ledwatt+"' WHERE ledname = '"+oldname+"'")
                            c.execute("UPDATE "+roomname+" SET ledname = '"+ledname+"' WHERE ledname = '"+oldname+"'")
                            #db.commit()
                            #update sqlite
                            conn.send("2>confirm\n")
                        elif cmp(cmd,"delete led")==0:#delete led
                            print data
                            roomname,lednumber,ledname=data.split(">")
                            c.execute("DELETE FROM "+roomname+" WHERE ledname='"+ledname+"'")
                            lednumber=int(lednumber)-1
                            c.execute("UPDATE Room SET roomlednumber="+str(lednumber)+" WHERE roomname='"+roomname+"'")
                            conn.send("3>confirm\n")
                        elif cmp(cmd,"countdown")==0:#countdown
                            ip, hour, mins= data.split("<")
                            print ip, hour, mins
                            thread.start_new_thread(countdown,(ip,int(hour),int(mins)))
                            conn.send("5>confirm\n")
                            
                        elif cmp(cmd,"get schedule list")==0:#get schedule list
                            #read from sqlite and send
                            c.execute("SELECT schedulename,status FROM Schedule")
                            schedule="0>" 
                            for i in c:
                                schedule+=i[0]+","+i[1]+"|"
                            print schedule
                            if cmp(schedule,"0>"):
                                schedule=schedule+"\n"
                                conn.send(schedule)
                            #conn.send("0>work,1|rest,1|sleep,0|\n")
                        elif cmp(cmd,"choose")==0:#activate a schedule
                            c.execute("SELECT schedulename,stime,etime,wd,we FROM Schedule WHERE schedulename='"+data+"'")
                            for i in c:
                                schedulename.append(i[0])
                                stime.append(i[1])
                                etime.append(i[2])
                                wd.append(i[3])
                                we.append(i[4])
                                print schedulename, stime,etime,wd,we
                            c.execute("UPDATE Schedule SET status = '1' WHERE schedulename ='"+data+"'")
                            print data,"her"
                            conn.send("1>confirm\n")
                        elif cmp(cmd,"unchoose")==0:#deactivate a schedule
                            c.execute("UPDATE Schedule SET status = '0' WHERE schedulename ='"+data+"'")
                            j=schedulename.index(data)
                            schedulename.pop(j)
                            stime.pop(j)
                            etime.pop(j)
                            wd.pop(j)
                            we.pop(j)
                            print data, "here"
                            conn.send("1>confirm\n")
                        elif cmp(cmd,"delete schedule")==0:#delete schedule
                            c.execute("DELETE FROM Schedule WHERE schedulename='"+data+"'")
                            c.execute("DROP TABLE schedule"+data)
                            j=schedulename.index(data)
                            schedulename.pop(j)
                            stime.pop(j)
                            etime.pop(j)
                            wd.pop(j)
                            we.pop(j)
                            print data
                            conn.send("2>confirm\n")
                        elif cmp(cmd,"get schedule")==0:#get schedule details
                            #get from sqlite
                            c.execute("SELECT stime,etime,wd,we FROM Schedule WHERE schedulename='"+data+"'")
                            sql="0>"
                            details=c.fetchone()
                            sql+=details[0]+","+details[1]+","+details[2]+","+details[3]+","
                            c.execute("SELECT led FROM "+"schedule"+data)
                            for i in c:
                                sql+=i[0]+"<"
                            print sql
                            conn.send(sql+"\n")
                            #conn.send("0>7:30,11:30,1,1,led1<led2<led5<\n")
                        elif cmp(cmd,"add schedule")==0:#add schedule
                            name,starttime,endtime,wdays,wends,ledlist=data.split("<")                            
                            c.execute("INSERT INTO Schedule(schedulename,stime,etime,wd,we,status) VALUES ('"
                                      +name+"','"+starttime+"','"+endtime+"','"+wdays+"','"+wends+"','1')")
                            schedulename.append(name)
                            stime.append(starttime)
                            etime.append(endtime)
                            wd.append(wdays)
                            we.append(wends)
                            c.execute("CREATE TABLE "+"schedule"+name+" (led TEXT PRIMARY KEY)")
                            led=ledlist.split(">")
                            for i in led:
                                k="INSERT INTO "+"schedule"+name+" (led) VALUES ('"+i+"')"
                                print k
                                c.execute(k)
                            conn.send("1>confirm\n")
                        elif cmp(cmd,"edit schedule")==0:#edit schedule
                            oldname,name,starttime,endtime,wdays,wends,ledlist=data.split("<")
                            if oldname in schedulename:
                                j=schedulename.index(oldname)	
                                schedulename[j]=name
                                stime[j]=starttime
                                etime[j]=endtime
                                wd[j]=wdays
                                we[j]=wends
                            c.execute("UPDATE Schedule SET stime='"+starttime+"' WHERE schedulename ='"+oldname+"'")
                            c.execute("UPDATE Schedule SET etime='"+endtime+"' WHERE schedulename ='"+oldname+"'")
                            c.execute("UPDATE Schedule SET wd='"+wdays+"' WHERE schedulename ='"+oldname+"'")
                            c.execute("UPDATE Schedule SET we='"+wends+"' WHERE schedulename ='"+oldname+"'")
                            c.execute("UPDATE Schedule SET schedulename='"+name+"' WHERE schedulename ='"+oldname+"'")
                            c.execute("DROP TABLE schedule"+oldname)
                            c.execute("CREATE TABLE schedule"+name+" (led TEXT PRIMARY KEY NOT NULL)")
                            led=ledlist.split(">")
                            for i in led:
                                if cmp(i,""):
                                    k="INSERT INTO schedule"+name+" VALUES ('"+i+"')"
                                    print k
                                    c.execute(k)
                            print data
                            conn.send("2>confirm\n")
                        elif cmp(cmd,"get consumption")==0:#get time and consumption
                            #get from sqlite
                            c.execute("SELECT roomname,roomlednumber FROM Room")
                            room=[]
                            for i in c:
                                room.append(i[0])
                            energytime=""
                            consumption=""
                            for j in room:
                                c.execute("SELECT ledwatt,totaltime FROM "+j)
                                roomtime=0
                                roomcon=0
                                t=""
                                con=""
                                count=0
                                for k in c:
                                    count+=1
                                    t+=k[1]+"<"
                                    e=int(k[0])*int(k[1])/1000
                                    con+=str(e)+"<"
                                    roomtime += int(k[1])
                                    roomcon+=e
                                if count==0:
                                    t="0"+"<"+t
                                else:
                                    t= str(roomtime/count)+"<"+t
                                con=str(roomcon)+"<"+con
                                energytime+=t
                                consumption+=con
                            print energytime                        
                            msg="0>"+energytime+","+consumption+"\n"
                            print msg
                            conn.send(msg)
                            #conn.send("0>540<300<240<230<200<30<230<230,430<330<100<55<33<22<145<145<\n")
                        elif cmp(cmd,"close")==0:#close connection
                            conn.send("98>socket closed\n")
                            conn.close()
                            print "socket closed"
                            state=0
                            Time_up=1
                        else:
                            print msg
                            conn.send("99>try again\n")
                    db.commit()
                state=0
if __name__ == '__main__':
    led_system()
