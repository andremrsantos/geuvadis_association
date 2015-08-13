#! /usr/bin/env python

__author__ = 'andresantos'

import MySQLdb, subprocess, numpy, os, re

from optparse import OptionParser
from yaml import load
from scipy import stats


class DB:
    __instance = None

    @staticmethod
    def instance():
        if DB.__instance is None:
            DB.__instance = DB()
        return DB.__instance

    def open(self, params):
        self.__db = MySQLdb.connect(
            host=params['host'],
            port=params['port'],
            user=params['user'],
            passwd=params['passwd'],
            db=params['db'])
        self.__cursor = self.__db.cursor()

    def close(self):
        self.__db.close()

    def query(self, query, *args):
        self.__cursor.execute(query, args)
        return self.__cursor.fetchall()

## GLOBAL ATTR
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

def load_genotype(path):
    samples = {}
    for line in open(path, 'r'):
        # print line.strip()
        fields = re.split("\s+", line.strip())
        id, sample = fields[0:2]
        genotype = sum( int(x) for x in fields[2:] )
        samples[sample] = genotype
    return samples


def count_genotype(set):
    count = [0, 0, 0]
    for i in set:
        count[i] += 1
    return count

def split(set, value):
    result = [ [], [], [] ]
    for i in range(len(set)):
        result[set[i]].append(value[i])
    return result


def main():
    ## Set script options
    parser = OptionParser("Use: %prog [options] snv-table\n"
                          "Please provide an snv table sorted table")
    parser.add_option("-p", "--params", dest="params",
                      help="YAML parameters file path",
                      default=os.path.join(SCRIPT_PATH, "config.yml"))
    parser.add_option("-v", "--vcf", dest="vcfs", help="1000 genomes vcfs folder path")
    (options, args) = parser.parse_args()

    ## Validates options
    if len(args) != 1:
        parser.error("Incorrect number of arguments")
    __params = load(open(options.params, 'r'))
    if options.vcfs is not None:
        __params['1000_genomes'] = options.vcfs

    ## Opening DB connection
    DB.instance().open(__params['db'])

    output = "/tmp/%d.tmp" % os.getpid()
    gt_script = "vcf query -f '[%ID %SAMPLE %GT\\n]' -r {0:}:{1:} {2:} | " \
                "grep {3:} | sed -E 's/[\\|\/]/ /g' > {4:}"
    vcf_path = "./{0:}/ALL.chr{1:}.*.vcf.gz".format(__params['1000_genomes'],
                                                    '%s')
    gv_query = "SELECT gene, sample, rpkm FROM gene_rpkm WHERE gene=%s"

    ## Checking 1000 genomes sample genotype
    __infile = open(args[0], 'r')

    ## INDEL data control
    last = -1
    samples = None

    print "##INDEL GENE N00 N01 N11 RHO PVALUE"

    for line in __infile:
        chr, pos, rsid, indel, gene = re.split("\s+", line.strip())
        
        if rsid == "." : rsid = "'\.'"

        ## IF current indel is different than previous,
        ## compute samples genotype
        if last != indel:
            last = indel

            path = vcf_path % chr
            cmd = gt_script.format(chr, pos, path, rsid, output)
            ## Call vcf query and wait return
            subprocess.call(cmd, shell=True)

            samples = load_genotype(output)

        ## Collect gene geuvadis data
        x = []
        y = []

        for entry in DB.instance().query(gv_query, gene):
            (gene, sample, rpkm) = entry

            if samples.has_key(sample):
                x.append(int(samples[sample]))
                y.append(float(rpkm))

        x = numpy.array(x)
        y = numpy.array(y)

        #print(x)

        ## IF gene has GEUVADIS data
        if len(x) > 0:
            count = count_genotype(x)
            n = sum(count)
            if(count[0] < n and count[1] < n and count[2] < n):
                #slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                rho, p_value = stats.mstats.spearmanr(x, y, use_ties = True)
            else:
                #slope, intercept, r_value, p_value, std_err = [numpy.NAN,numpy.NAN,numpy.NAN,-1,0]
                rho, p_value = [0,-1]
            #sp = split(x,y)
            #result = ""
            # count = count_genotype(x)
            #for i in range(3):
            #    for j in range(i+1,3):
            #        # print sp[i]
            #        # print sp[j]
            #        if count[i] == 0 or count[j] == 0:
            #            result += "%dx%d:nan " % (i,j)
            #        else:
            #            d, p = stats.ks_2samp(numpy.array(sp[i]), numpy.array(sp[j]))
            #            result += "%dx%d:%.5f " % (i,j,p)
            ## Output results
            #print "{0:} {1:} {7:03d} {8:03d} {9:03d} {2:5.5f} " \
            #      "{3:5.5f} {4:5.5f} {5:5.5f} {6:5.5f}".format(
            #    indel, gene, slope, intercept, r_value, p_value, std_err,
            #    count[0], count[1], count[2])
            print "{0:} {1:} {2:03d} {3:03d} {4:03d} {5:5.5f} {6:.5g}".format(
                rsid, gene, count[0], count[1], count[2], float(rho), float(p_value))
            #print "{0:} {1:} {2:03d} {3:03d} {4:03d} {5:} ".format(
            #    indel, gene, count[0], count[1], count[2], result)
        else:
            print "{0:} {1:} X X X {2:5.5f} {3:5.5f}".format(indel, gene, float(0), float(-1))

    ## Closing DB connection
    DB.instance().close()

    ## Remove any tmp file
    subprocess.call("rm %s" % output, shell=True)

if __name__ == "__main__":
    main()
