# -*- coding: utf-8 -*-

import subprocess, re

gre=re.compile(r"\((\w+) (\w+)\)",re.M+re.U+re.I)

def zhparse(filename):
	""" parse utf8 encoded file
	give back couples word, pos
	"""
	a = subprocess.check_output('java -mx1500m -cp parser/stanford-parser.jar edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8 parser/xinhuaFactoredSegmenting.ser.gz {filename}'.format(filename=filename), shell=True, stderr=subprocess.STDOUT).decode("utf-8")
	for aa in a.split("\n\n"):
		for m in gre.finditer(aa):
			print "o"
			yield (m.group(1),m.group(2))
		yield (None,None)
		



#a=u"""(ROOT
  #(IP
    #(IP
      #(NP (NR 新华))
      #(VP (VV 网北京)
        #(NP
          #(NP (NT ５月) (NT ２１日))
          #(NP (NN 电) (NN 特稿)))))
    #(PU ：)
    #(IP
      #(LCP
        #(NP (NN 元首) (NN 会晤引领))
        #(LC 中))
      #(NP
        #(NP (NR 美))
        #(NP (NN 关系)))
      #(VP
        #(NP (NT 未来))
        #(VP (VV ()
          #(NP (NN 记者) (NN 包尔文) (NN 赵卓昀) (NN 刘健) (NN 陈静) (NN )))
          #(QP
            #(NP (NT ２０１３年) (NT ６月))
            #(NP (NT ７日)
              #(CC 至)
              #(NT ８日))))))
    #(PU ，)
    #(IP
      #(NP
        #(NP (NR 中) (NR 美))
        #(NP (NN 关系)))
      #(VP
        #(ADVP (AD 将))
        #(VP (VV 迎来)
          #(NP
            #(QP (CD 一)
              #(CLP (M 个)))
            #(ADJP (JJ 历史性))
            #(NP (NN 时刻))))))
    #(PU ——)
    #(IP
      #(NP (NR 中国) (NN 国家) (NN 主席) (NN 习近平))
      #(VP
        #(ADVP (AD 将))
        #(PP (P 同)
          #(NP
            #(NP (NR 美国))
            #(NP (NN 总统) (NN 奥巴马))))
        #(PP (P 在)
          #(NP
            #(NP (NR 美国))
            #(NP (NN 加利福尼亚州))))
        #(VP (VV 举行)
          #(NP (NN 会晤)))))
    #(PU 。)))

#(ROOT
  #(IP
    #(NP (PN 这))
    #(VP (VC 是)
      #(UCP
        #(IP
          #(NP
            #(NP (NR 中) (NR 美))
            #(QP (CD 两))
            #(NP (NN 国)))
          #(VP
            #(VP (VV 完成)
              #(NP (NN 领导) (NN 层)))
            #(VP (VV 换届))))
        #(PU 、)
        #(NP
          #(DNP
            #(LCP
              #(IP
                #(NP
                  #(NP
                    #(QP (CD 两))
                    #(NP (NN 国)))
                  #(NP (NN 关系)))
                #(VP (VV 进入)
                  #(NP
                    #(ADJP (JJ 新))
                    #(NP (NN 时期)))))
              #(LC 后))
            #(DEG 的))
          #(QP (OD 首)
            #(CLP (M 次)))
          #(NP (NN 国家) (NN 元首) (NN 会晤)))))
    #(PU 。)))
#"""


#if already segmented:
#run("java -mx500m -cp stanford-parser.jar edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8 chineseFactored.ser.gz data/chinese-onesent-unseg-utf8.txt")
# if not
#run("java -mx500m -cp stanford-parser.jar edu.stanford.nlp.parser.lexparser.LexicalizedParser -encoding utf-8 xinhuaFactoredSegmenting.ser.gz zh.utf-8")

if __name__ == "__main__":
	#zhparse("zh.utf-8")
	for (w,c) in zhparse("zh.utf-8"):
		print w,c