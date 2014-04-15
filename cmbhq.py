#coding: utf-8


import httplib
import struct
import time
import lxml.etree

"""
版本 3-                   2
Header 0-                 2
AMF主体 1                 2
请求长度 v                2
请求字符串                v
Target长度 v2             2
Target字符串              v2
内容长度    v3            4
内容字符串                v3   
"""

"""
public enum DataType
{
   Number = 0,
   Boolean = 1,
   String = 2,
   UntypedObject = 3,
   MovieClip = 4,
   Null = 5,
   Undefined = 6,
   ReferencedObject = 7,
   MixedArray = 8,
   End = 9,
   Array = 10,//0x0A
   Date = 11,//0x0B
   LongString = 12,//0x0C
   TypeAsObject = 13,//0x0D
   Recordset = 14,//0x0E
   Xml = 15,//0x0F
   TypedObject = 16,//0x10
   AMF3data=17//0x11
}
"""

class dapanhq:
    def __init__(self, ctx):
        root = lxml.etree.fromstring(ctx)
        rt=[]
        for dp in root.iter('dp'):
            tx = dp.text
            lst = tx.split('|')
            
            for k in lst:
                d=[]
                vs = k.split(',')
                for viter in vs:
                    d.append(float(viter) )
                rt.append(d)
        self.data = rt
class sshq:
    NameList=['昨收','今开', '现价', '总量','总额','最高','最低','涨跌','涨幅',
            '内盘','外盘','n1','买1','买2','买3','买4','买5','b1','b2','b3','b4','b5',
            '卖1','卖2','卖3','卖4','卖5','s1','s2','s3','s4','s5','n2','n3','n4']
    def __init__(self, ctx=None):
        self.data=[]
    def parse(self, ctx):
        root = lxml.etree.fromstring(ctx)
        tm = ''
        for mt in root.iter('mt'):
            tm = '%02d:%02d' % ( int(mt.text) / 60, int(mt.text) %60)
        for ct in root.iter('ct'):
            hq = ct.text
            lst = hq.split(',')
            
            print tm,'\t',
            for k in range(len(lst)):
                print NameList[k], float(lst[k]),'\t',
            print 
def printResponse(res):
    print 'version:', res.version
    print 'reason:', res.reason
    print 'status:', res.status
    print 'msg:', res.msg
    print 'headers:', res.getheaders()
def printHex(str):
    pstr = ''
    for i in range(len(str)):
        if str[i] >= 'a' and str[i] <= 'z':
            pstr += str[i]
        elif str[i] >= 'A' and str[i] <= 'Z':
            pstr += str[i]
        elif str[i] in ' 0123456789.,+-_/*\\()`~!@#$%^&[]{}|?<>;:\'"' :
            pstr += str[i]
        else:
            pstr += hex( ord( str[i] ) )[2:].rjust(2, '0')
    print pstr
def reverse(str):
    rstr = ''
    size = len(str)
    for i in range(size,0,-1):
        rstr += str[i-1]
    return rstr

def packint(i4):
    return reverse( struct.pack('I', i4) )
def packshort(i2):
    return reverse( struct.pack('H', i2) )
def packdouble(d8):
    return reverse( struct.pack('d', d8) )

def unpackshort(i2):
    return struct.unpack('H', reverse(i2[0:2]) )[0]
def unpackint(i4):
    return struct.unpack('I', reverse(i2[0:4]) )[0]
def unpackdouble(d8):
    return struct.unpack('d', reverse(d8[0:8]) )[0]
class amfpackage:
    def __init__(self):
        self.version = 3
        self.header = 0
        self.bodylen = 1
        self.reqlen = 0
        self.req = ''
        self.target = ''
        self.targetlen = 0
        self.ctx = ''
        self.ctxlen = 0
        self.targetid = 100
    def nextTarget(self):
        self.targetid += 1
        return self.targetid
    def parseResponse(self, r):
        self.version = unpackshort(r)
        self.header = unpackshort(r[2:])
        self.bodylen = unpackshort(r[4:])
        self.reqlen = unpackshort(r[6:])
        self.req = r[8:8+self.reqlen]
        pos = 8 + self.reqlen
        self.target = r[pos:pos+6]
        self.targetlen = 6
        pos += 6
        if r[pos] == '\x00':
            pos += 1
            self.ctx = r[pos:]
            self.ctxlen = len(r[pos:])
        else:
            pos += 1
            self.ctxlen = unpackshort(r[pos:])
            pos += 2
            self.ctx = r[pos:]
    def insertString(self, s):
        r = ''
        r += packshort( len(s) )
        r += s
        return r
    def insertStringArray(self,a):
        r = packint(len(a))
        for k in a:
            r += '\x02'
            r += self.insertString(k)
        return r
    def getMinuteTime(self):
        dt = '\x0A' #object
        dt += packint(0)
        return genrequest('hq.getMinuteTime', self.nextTarget(), dt)
    def getAllStockAndSession(self):
        dt = '\x0A' #object
        dt += self.insertStringArray(['59.66.253.25', '10.0.24.191', '5EA92645-6AD2-49D8-B933-862F4962F0B4', '', ''])
        #dt = packint( len(dt) ) + dt
        
        return genrequest('hq.getAllStockAndSession', self.nextTarget(), dt)
    def flashHQList_inner(self, codelist):
        dt = '\x0A' #object
        dt += self.insertStringArray([codelist, 'push'])
        return genrequest('hq.flashHQList_inner', self.nextTarget(), dt)
    def getInitStatus(self):
        dt = '\x0A' #object
        dt += packint(0)
        return genrequest('hq.getInitStatus', self.nextTarget(), dt)
    def dapan(self):
        """ 当前大盘 """
        dt = '\x0A' #object
        dt += self.insertStringArray(['3SYELHLKJUW68VQI'])
        return genrequest('hq.dapan', self.nextTarget(), dt)
    def refreshSSHQ_2(self, codelist):
        dt = '\x0A'
        req = []
        ctx = []
        targetid = []
        for code in codelist:
            dt='\x0A'
            dt += self.insertStringArray([code, '0'])
            req.append('hq.refreshSSHQ')
            targetid.append(self.nextTarget())
            ctx.append(dt)
        return genrequest(req, targetid, ctx)
    def refreshSSHQ(self, code):
        """ 实时行情 """
        dt = '\x0A' #object
        dt += self.insertStringArray(code)#[code, '0']
        return genrequest('hq.refreshSSHQ', self.nextTarget(), dt)
    def refreshFBCJ(self, code):
        """ 分笔成交 """
        dt = '\x0A'
        dt += self.insertStringArray([code, '0'])
        return genrequest('hq.refreshFBCJ', self.nextTarget(), dt)
    def getXXDLList(self, code):
        dt = '\x0A' #object
        dt += self.insertStringArray([code, 'sshq'])
        return genrequest('hq.getXXDLList', self.nextTarget(), dt)
    def lastHQ(self, code):
        """ 当前行情 """
        dt = '\x0A' #object
        dt += self.insertStringArray([code, '0', '-1'])
        return genrequest('hq.lastHQ', self.nextTarget(), dt)
def genrequest(req, targetid, ctx):
    
    r = ''
    r += packshort(3)
    r += packshort(0)
    
    if type(req) is list:
        r += packshort(len(req))
        for i in range(len(req)):
            target = '/' + str(targetid[i])
            r += packshort( len(req[i]) )
            r += req[i]
            r += packshort( len(target) )
            r += target
            r += packint( len(ctx[i]) )
            r += ctx[i]
    else:
        target = '/' + str(targetid)
        r += packshort(1)
        r += packshort( len(req) )
        r += req
        r += packshort( len(target) )
        r += target
        r += packint( len(ctx) )
        r += ctx
    return r

def ongetMinuteTime(ctx):
    #000300000001000b/1/onResult0000ffffffff00@96t0000000000
    d = unpackdouble(ctx)
    i = int(d)
    lc = time.localtime()
    print 'Local  time: %04d-%02d-%02d %02d:%d' % (lc.tm_year, lc.tm_mon, lc.tm_mday, lc.tm_hour, lc.tm_min)
    print 'Server time: %04d-%02d-%02d %02d:%d' % (lc.tm_year, lc.tm_mon, lc.tm_mday, i / 60,i%60)
def postdt():
    conn = httplib.HTTPConnection("hq.newone.com.cn")
    body = ''
    #headers['Referer'] = "http://hq.newone.com.cn/"
    headers = {'Content-Type':'application/x-amf',
    'Host':	'hq.newone.com.cn', 
'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0', 
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Encoding':	'gzip, deflate',
'Accept-Language':	'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
'Connection':	'keep-alive'};
    conn.close()
    """
    conn.request("get", "/", headers = headers)
    res = conn.getresponse()

    if res.status != 200:
        printResponse(res)
        return

    hs = res.getheaders()
    msg = res.read()
    for k in hs:
        if k[0] == 'set-cookie':
            p = k[1].find(';')
            c = k[1][:p]
            headers['Cookie'] = c
    #headers['Cookie'] += '; authorid=5EA92645-6AD2-49D8-B933-862F4962F0B4'
    #print headers
    """
    
    pkg = amfpackage()
    
    """
    body = pkg.getMinuteTime()
    f=open("t.dat", "wb")
    f.write(body)
    f.close()
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    print res.getheaders()
    printHex(msg)
    
    
    #pkg.parseResponse(msg)
    #ongetMinuteTime(pkg.ctx)
    #print pkg.req,pkg.ctxlen,unpackdouble(pkg.ctx)
    #return
    
    body =pkg.getAllStockAndSession()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    ##pkg.parseResponse(msg)
    ##printHex(msg)
    f= open('AllStockAndSession.xml', 'w')
    f.write(msg[0x33+0x4a:])
    f.close()
    
    return
    """
    
    """

    print "pkg.flashHQList_inner"
    body = pkg.flashHQList_inner('sz000001,sz000002')
    fb = open("flashHQList_inner_body.bin","wb")
    fb.write(body)
    fb.close()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    #printHex(msg)
    #pkg.parseResponse(msg)
    print pkg.req,pkg.ctx
    f= open('flashHQList_inner.bin', 'wb')
    f.write(msg)
    f.close()
    return
    """
    
    
    print "pkg.refreshSSHQ"
    body = pkg.refreshSSHQ(['sz000001','sz000002'])
    fb = open("refreshSSHQ_body.bin","wb")
    fb.write(body)
    fb.close()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    #printHex(msg)
    #pkg.parseResponse(msg)
    print pkg.req,pkg.ctx
    f= open('refreshSSHQ.bin', 'wb')
    f.write(msg)
    f.close()
    return
    
    
    """
    print "pkg.refreshSSHQ"
    body = pkg.refreshSSHQ_2(['sz000001','sz000002'])
    fb = open("refreshSSHQ_2_body.bin","wb")
    fb.write(body)
    fb.close()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    #printHex(msg)
    #pkg.parseResponse(msg)
    print pkg.req,pkg.ctx
    f= open('refreshSSHQ_2.bin', 'wb')
    f.write(msg)
    f.close()
    return
    """
    
    """
    print "dapan"
    body = pkg.dapan()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    pkg.parseResponse(msg)
    print pkg.req,pkg.ctx
    dhq=dapanhq(pkg.ctx)
    print dhq.data
    """
    
    """
    print "getInitStatus"
    body = pkg.getInitStatus()
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    print len(msg)
    pkg.parseResponse(msg)
    print pkg.req,pkg.ctx
    f= open('getInitStatus.xml', 'w')
    f.write(pkg.ctx)
    f.close()
    return
    """
    
    """
    ctx = ''
    print "pkg.refreshFBCJ"
    while(1):
        t1 = time.time()
        body = pkg.refreshFBCJ('sz000001')
        #printHex(body)
        conn.request("post", "/messagebroker/amf", body, headers)
        res = conn.getresponse()
        msg = res.read()
        pkg.parseResponse(msg)
        t2 = time.time() - t1
        if t2 < 0.5:
            time.sleep(0.5 - t2)
        if ctx == pkg.ctx :
            print pkg.req
            continue
        else:
            ctx = pkg.ctx
            print pkg.req,pkg.ctx
    
    print "lastHq"
    body = pkg.lastHQ('sz000001')
    #printHex(body)
    conn.request("post", "/messagebroker/amf", body, headers)
    res = conn.getresponse()
    msg = res.read()
    pkg.parseResponse(msg)
    #print pkg.req,pkg.ctx
    f= open('sz000001_sshq.xml', 'w')
    f.write(pkg.ctx)
    f.close()
    
    sq = sshq()
    while(1):
        t1 = time.time()
        print "pkg.refreshSSHQ"
        body = pkg.refreshSSHQ('sz000001')
        #printHex(body)
        conn.request("post", "/messagebroker/amf", body, headers)
        res = conn.getresponse()
        msg = res.read()
        pkg.parseResponse(msg)
        sq.parse(pkg.ctx)
        #print pkg.req,pkg.ctx
        t2 = time.time() - t1
        if t2 < 2:
            time.sleep(2 - t2)
    
    conn.close()
    """
if __name__ == "__main__":
    postdt()
    
    
