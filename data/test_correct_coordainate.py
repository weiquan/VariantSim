import sys
import bisect
import read_ann
#from readfq import readfq
#convert wgsim sim fastq to sim pos  
#awk '/@/{split(substr($0,2), a, "_");print a[1], a[2], a[3] }' read.fq

def createPosMap(ann, posRefStart, posRefEnd, posSimStart, posSimEnd):
    '''create postion map'''
    posRefStart.setdefault(ann.ref_chr, []).append(ann.ref_start)
    posRefEnd.setdefault(ann.ref_chr, []).append(ann.ref_end)
    posSimStart.setdefault(ann.ref_chr, []).append(ann.sim_start)
    posSimEnd.setdefault(ann.ref_chr, []).append(ann.sim_end)


def simPos2Ref( chrom, posInSim,
                posRefStart, posRefEnd, 
                posSimStart, posSimEnd):
    '''convert pos in simulate genome coord to orignal genome coord'''
    posSimStartVec = posSimStart[chrom]
    posSimEndVec = posSimEnd[chrom]
    posRefStartVec = posRefStart[chrom]
    posRefEndVec = posRefEnd[chrom]
    
    eventPosInRef, eventPosInRef, ret_pos = 0, 0, 0

    i = bisect.bisect_right(posSimStartVec, posInSim)
    l_posRef = len(posSimStartVec)

    if i > l_posRef:
        print >>sys.stderr, '%d > len(posRef) %d' % (i, l_posRef)
        print >>sys.stderr, i
        sys.exit(1)
    elif i == 0:
        eventPosInRef = posRefStartVec[i]
        eventPosInSim = posSimStartVec[i]
        ret_pos = eventPosInRef - (eventPosInSim - posInSim)
    elif i < l_posRef:
        if posSimEndVec[i-1] <= posInSim:
            eventPosInRef = posRefStartVec[i]
            eventPosInSim = posSimStartVec[i]
            ret_pos = eventPosInRef - (eventPosInSim - posInSim)
        elif posInSim == posSimStartVec[i-1]:
            eventPosInRef = posRefStartVec[i-1]
            eventPosInSim = posInSim
            ret_pos = eventPosInRef - (eventPosInSim - posInSim)
        elif posInSim > posSimStartVec[i-1]:
            #
            if posSimEndVec[i-1] - posSimStartVec[i-1] ==\
               posRefEndVec[i-1] - posRefStartVec[i-1]:
                pass
            # DEL
            elif posSimEndVec[i-1] - posSimStartVec[i-1] == 1 and\
                    posRefEndVec[i-1] - posRefStartVec[i-1] > 1:
                print >>sys.stderr, 'Pos shouldn\'t be in DEL region'
                print posInSim, posSimEndVec[i-1], posSimStartVec[i-1]

                sys.exit(1)
            # INS 
            elif posRefEndVec[i-1] - posRefStartVec[i-1] == 1 and\
                    posSimEndVec[i-1] - posSimStartVec[i-1] > 1:
                #eventPosInRef = posRefEndVec[i-1]
                #eventPosInSim = posSimEndVec[i-1]
                #ret_pos = eventPosInRef - (eventPosInSim - posInSim)
                ret_pos = posRefEndVec[i-1]
            else:
                print >>sys.stderr, '[Pos Error0]: posInSim = %d' % (posInSim)
                print >>sys.stderr, 'posSimStartVec[i-1] = %d' % \
                                    (posSimStartVec[i-1])
                print >>sys.stderr, 'posSimEndVec[i-1] = %d' % \
                                    (posSimEndVec[i-1])
                print >>sys.stderr, 'posSimStartVec[i] = %d' % \
                                    (posSimStartVec[i])
                print >>sys.stderr, 'posSimEndVec[i] = %d' % \
                                    (posSimEndVec[i])
                sys.exit(1)
        else:
            print >>sys.stderr, '[Pos Convert Error]'
            print >>sys.stderr, posInSim
            sys.exit()
    else:   # i == l_posRef
        if posSimEndVec[i-1] <= posInSim:
            ret_pos = posRefEndVec[i-1] + posInSim - posSimEndVec[i-1]
        elif posSimEndVec[i-1] == posInSim:
            ret_pos = posRefEndVec[i-1]
        elif posSimStartVec[i-1] == posInSim:
            ret_pos = posRefStartVec[i-1]
        else:  # posSimEndVec[i-1] > posInSim
            #
            if posSimEndVec[i-1] - posSimStartVec[i-1] ==\
               posRefEndVec[i-1] - posRefStartVec[i-1]:
                pass
            #DEL
            elif posSimEndVec[i-1] - posSimStartVec[i-1] == 1 and\
                    posRefEndVec[i-1] - posRefStartVec[i-1] > 2:
                print >>sys.stderr, 'Pos shouldn\'t be in DEL region'
                print posInSim, posSimEndVec[i-1], posSimStartVec[i-1]

                sys.exit(1)
            #INS
            elif posRefEndVec[i-1] - posRefStartVec[i-1] == 1 and\
                    posSimEndVec[i-1] - posSimStartVec[i-1] > 2:
                eventPosInRef = posRefEndVec[i-1]
                eventPosInSim = posSimEndVec[i-1]
                ret_pos = eventPosInRef - (eventPosInSim - posInSim)
            else:
                print >>sys.stderr, '[Pos Error1]: posInSim = %d' % (posInSim)
                print >>sys.stderr, 'posSimStartVec[i-1] = %d' % \
                                    (posSimStartVec[i-1])
                print >>sys.stderr, 'posSimEndVec[i-1] = %d' % \
                                    (posSimEndVec[i-1])
                print >>sys.stderr, 'posSimStartVec[i] = %d' % \
                                    (posSimStartVec[i])
                print >>sys.stderr, 'posSimEndVec[i] = %d' % \
                                    (posSimEndVec[i])
                sys.exit(1)
    # if i < l_posRef-1:
    #     if eventPosInSim > posSim and posSimStartVec[i+1] >posSim and\
    #         eventPosInSim - posSim >= posSimStartVec[i+1] -posSim:
    #         print chrom, posInSim, eventPosInSim, eventPosInRef,\
    #                eventPosInRef - (eventPosInSim - posInSim)
    return ret_pos

#INPUT: read.fq ann
usage = \
    'simPos2Ref.py <SimPosAns> <Ann> '
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >>sys.stderr, usage
        sys.exit(1)
    #fp_in_r1 = open(sys.argv[1], 'r')
    #fp_in_r2 = open(sys.argv[2], 'r')
    fp_simPos = open(sys.argv[1], 'r')
    fp_ann = open(sys.argv[2], 'r')
    #fp_out_r1 = open(sys.argv[5] + '1.fq', 'w')
    #fp_out_r2 = open(sys.argv[5] + '2.fq', 'w')
    #fp_ans = open(sys.argv[5] + '.ans', 'w')
    #Read Ann
    posRefStart, posSimStart, posRefEnd, posSimEnd = {}, {}, {}, {}
    for line in fp_ann:
        a = read_ann.ann(line)
        createPosMap(a, posRefStart, posRefEnd, posSimStart, posSimEnd)
        #print posRefEnd, posSimEnd
    #convert read1
    tot_num = 0
    for line in fp_simPos:
        line = line.strip()
        chrom, simPos= line.split()
        simPos= int(simPos)
        refPos = simPos2Ref(chrom, simPos,
                             posRefStart, posRefEnd,
                             posSimStart, posSimEnd)
        print '[CHROM:%s]%s->%s'%(chrom, simPos, refPos)
        
    fp_ann.close()
    fp_simPos.close()



