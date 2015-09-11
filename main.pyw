from socket import *
from tkinter import *
from threading import *
from bf import BF
from help import Help
import time
import random

hlp = Help()

class Window(Frame):
    def __init__(self, master = None, conn = None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.conn = conn

    def onSend(self, messg):
        self.conn.SendMessage(self.conn, messg)

    def modified(self, event):
        self.RichTextBox1.see(END)

    def rest(self):
        self.RichTextBox1.edit_modified(False)
        
    def createWidgets(self):
        self.RichTextBox1 = Text(self)
        self.Label1 = Label(self)
        self.ListBox1 = Listbox(self)
        self.Label1["text"] = "Virgo IRC"
        self.Label1.pack(side = BOTTOM, fill = Y)
        self.ListBox1.pack(side = RIGHT, fill = Y)
        self.Tb1Var = StringVar()
        self.TextBox1 = Entry(self, textvariable = self.Tb1Var, width=77)
        self.TextBox1.pack(side = BOTTOM)
        self.RichTextBox1.edit_modified(False)
        self.ScrollBar1 = Scrollbar(self)
        self.ScrollBar1.config(command = self.RichTextBox1.yview)
        self.RichTextBox1.config(yscrollcommand = self.ScrollBar1.set)
        self.ScrollBar1.pack(side = RIGHT, fill = Y)
        self.RichTextBox1.bind("<<Modified>>", self.modified)
        self.RichTextBox1.pack(side = LEFT, fill = Y)
        self.RichTextBox1["width"] = 64

class Connection:
    def __init__(self):
        self.Host = "irc.freenode.net"
        self.Port = 6667
        self.Buf  = 1024
        self.Channel = "#virgo-test"
        self.Address = (self.Host, self.Port)
        self.Channels = [self.Channel]
        self.Nick = "VirgoBeta"
        self.Username = self.Nick + " 0 * :" + self.Nick
        self.CallbackProcess = None
        self.Evaluators = {"bf":[]}

    def SendMessage(self, s, receiver):
        self.Tcp.send( bytes("PRIVMSG " + receiver + " :" + s +"\r\n", "utf-8") )

    def Connect(self):
        # connect to irc!
        self.Tcp = socket(AF_INET, SOCK_STREAM)
        self.Tcp.connect(self.Address)

    def RegisterProcessEvent(self, func):
        # event handler!
        self.CallbackProcess = func

    def Authorize(self):
        # authorization
        messg = "NICK " + self.Nick + "\r\n"
        self.Tcp.send( bytes(messg, "utf-8") )
        messg = "USER " + self.Username + "\r\n"
        self.Tcp.send( bytes(messg, "utf-8") )
        time.sleep(3)
        messg = "JOIN " + self.Channel + "\r\n"
        self.Tcp.send( bytes(messg, "utf-8") )
        messg = "PASS " + "555333666\r\n"
        self.Tcp.send( bytes(messg, "utf-8") )
        messg = "PRIVMSG Virgolang :/join " + self.Channel + "\r\n"
        self.Tcp.send( bytes(messg, "utf-8") )

    def Process(self, data):
        if self.CallbackProcess != None:
            self.CallbackProcess(data)

    def Collect(self):
        while 1:
            try:
                data = self.Tcp.recv(self.Buf)
                data = data.strip(b'\r\n')
                pdata = data.decode("utf-8")
                if not pdata == "":
                    self.Process(pdata)
            except:
                pass

class WorkerThread(Thread):
    def __init__(self, master, connectivity, threadID, name):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.master = master
        self.connectivity = connectivity

    def privmsg(self, sender, content, where):
        print(sender)
        print(content)
        print(where)
        if content.startswith("&"):
            cmd = content[1:]
            if cmd.split(" ")[0] == "join":
                self.connectivity.Tcp.send( bytes("PART " +self.connectivity.Channel+ " :\"Changing channel.\""+"\r\n", "utf-8") )
                self.connectivity.Channel = content[1:].split(" ")[1]
                self.connectivity.Tcp.send( bytes("JOIN "+self.connectivity.Channel+"\r\n", "utf-8") )
            elif cmd.split(" ")[0] == "hi" or cmd == "hi":
                try:
                    if cmd.split(" ") != "":
                        self.connectivity.SendMessage("Hi, %s! (from %s)" % (cmd.split(" ")[1],sender), self.connectivity.Channel)
                    else:
                        self.connectivity.SendMessage("Hi, %s!" % (sender), self.connectivity.Channel)
                except:
                    self.connectivity.SendMessage("Hi, %s!" % (sender), self.connectivity.Channel)
            elif cmd.split(" ")[0] == "help":
                try:
                    hlp = Help()
                    tp = cmd.split(" ")[1]
                    print("Topic %s"%tp)
                    outp = hlp.requestHelp(tp)
                    for ln in outp:
                        self.connectivity.SendMessage(ln, self.connectivity.Channel)
                except:
                    outp = hlp.requestTopics()
                    self.connectivity.SendMessage(outp, self.connectivity.Channel)

            elif cmd.split(" ")[0] == "bf":
                cmdpt = "".join(cmd.split(" ")[1:])
                bfe = BF(False, True)
                outpst = ""
                if cmdpt.find(",") != -1:
                    outpst = "No inputs."
                else:
                    outpst = bfe.evaluate(cmdpt)
                if outpst == -8192 or outpst == "-8192":
                    outpst = "Loop protection. "
                outpst = outpst.replace("\n"," \\ ")
                self.connectivity.SendMessage("-> %s" % outpst, self.connectivity.Channel)
                
            else:
                self.connectivity.SendMessage("%s is not implemented. Sorry." % cmd.split(" ")[0], self.connectivity.Channel)
        else:
            pass
    def procreceive(self, data):
        self.master.RichTextBox1.insert(END, data)
        self.master.rest()
        if data.startswith(":"):
            #try:
                if data[1:].split(" :")[0].split(" ")[1] == "PRIVMSG":
                    if data[1:].split(" :")[0].split(" ")[2] == "VirgoIrcB":
                        self.privmsg(data[1:].split(" :")[0].split(" ")[0].split("!")[0], data[1:].split(" :")[1], "")
                    else:
                        self.privmsg(data[1:].split(" :")[0].split(" ")[0].split("!")[0], data[1:].split(" :")[1], data[1:].split(" :")[0].split(" ")[2])
            #except:
            #    print("Exception :/")
        elif data.startswith("PING :"):
            self.connectivity.Tcp.send( bytes("PONG :" + data.split(" :")[1] + "\r\n", "utf-8") )
            print("Pong!")

    def run(self):
        self.master.RichTextBox1.insert(END, "Started %s Thread #%s\n" %(self.name,self.threadID))
        self.connectivity.RegisterProcessEvent(self.procreceive)
        self.connectivity.Connect()
        self.connectivity.Authorize()
        self.connectivity.Collect()
        
MC = Tk()
MC.wm_title("Virgo IRC")
DS = Connection()
DC = Window(master = MC, conn = DS)
WT = WorkerThread(DC, DS, "1", "Receiver")
WT.start()
DC.mainloop()
