from socket import *
from tkinter import *
from threading import *
from bf import BF
from help import Help
import time
import random

# The help module
hlp = Help()

class Window(Frame):
    def __init__(self, master = None, conn = None): # conn is connection object.
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.conn = conn

    def onSend(self, messg):
        # Connection.SendMessage(self, messg)
        self.conn.SendMessage(self.conn, messg)

    def modified(self, event):
        # For scrolling down log box.
        self.RichTextBox1.see(END)

    def rest(self):
        # For firing of Window.modified event.
        self.RichTextBox1.edit_modified(False)
        
    def createWidgets(self):
        self.RichTextBox1 = Text(self)                                      # Log box.
        self.Label1 = Label(self)                                           # Bottom status label.
        self.ListBox1 = Listbox(self)                                       # Peer list. Not implemented.
        self.Label1["text"] = "Virgo IRC"                                   # Initial text of status label.
        self.Label1.pack(side = BOTTOM, fill = Y)                           # Add status label to bottom.
        self.ListBox1.pack(side = RIGHT, fill = Y)                          # Add peer list to right.
        self.Tb1Var = StringVar()                                           # Content of entry box.
        self.TextBox1 = Entry(self, textvariable = self.Tb1Var, width=77)   # Entry box for sending messages from bot.
        self.TextBox1.pack(side = BOTTOM)                                   # Add entry box.
        self.RichTextBox1.edit_modified(False)                              # Required for event firing.
        self.ScrollBar1 = Scrollbar(self)                                   # Scrollbar for log box.
        self.ScrollBar1.config(command = self.RichTextBox1.yview)           # Configure scrollbar
        self.RichTextBox1.config(yscrollcommand = self.ScrollBar1.set)      # Configure log box.
        self.ScrollBar1.pack(side = RIGHT, fill = Y)                        # Add scroll bar.
        self.RichTextBox1.bind("<<Modified>>", self.modified)               # Bind the event.
        self.RichTextBox1.pack(side = LEFT, fill = Y)                       # Add the log box.
        self.RichTextBox1["width"] = 64                                     # Specify the width.

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
        #messg = "PRIVMSG Virgolang :/join " + self.Channel + "\r\n" # no bombards!
        #self.Tcp.send( bytes(messg, "utf-8") )

    def Process(self, data):
        if self.CallbackProcess != None:
            self.CallbackProcess(data) # callback from worker thread.

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
        if content.startswith("&"): # command.
            cmd = content[1:] # strip the &.
            if cmd.split(" ")[0] == "join":
                self.connectivity.Tcp.send( bytes("PART " +self.connectivity.Channel+ (" :Changing channel to '%s'."%cmd.split(" ")[1])+"\r\n", "utf-8") )
                self.connectivity.Channel = content[1:].split(" ")[1] #= cmd.split(" ")[1]
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
            if data[1:].split(" :")[0].split(" ")[1] == "PRIVMSG":
                self.privmsg(data[1:].split(" :")[0].split(" ")[0].split("!")[0], data[1:].split(" :")[1], data[1:].split(" :")[0].split(" ")[2])
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
