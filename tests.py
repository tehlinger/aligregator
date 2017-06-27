import unittest
import pprint
import numpy as np
from collections import OrderedDict

from chunks_loader import *
from stats import *
from aggregator import *
from time_analyzer import *

def print_debug(a,b):
    print("\n================EXPECTED==============")
    print(a)
    print("================  GOT  ==============")
    print(b)

class TestChunkLoad(unittest.TestCase):

    def test_load_chunk_bounds(self):
        chunk0 = load_chunk(0,"data/pcFoo.dat")
        chunk1 = load_chunk(1,"data/pcFoo.dat")

        self.assertEqual(chunk0.bounds[0],5.0)
        self.assertEqual(chunk0.bounds[1],10.0)
        self.assertEqual(chunk1.bounds[0],10.0)
        self.assertEqual(chunk1.bounds[1],15.0)

    def test_segs_object(self):
        segs = Seg_manager(["0","1","2","3"])

        self.assertEqual(segs.has_intermediates(),True)
        self.assertEqual(segs.num_segs,3)
        self.assertEqual(segs.get_id(0,1),"0:1")

    def test_load_chunk_packets(self):
        chunk0 = load_chunk(0,"data/pcFoo.dat")
        chunk1 = load_chunk(1,"data/pcFoo.dat")

        self.assertIsNotNone(chunk0.data['mpls:22'])
        self.assertIsNotNone(chunk1.data['mpls:22'])
        self.assertEqual(chunk0.data['mpls:22'],self.chunkfoo_0.data['mpls:22'])
        self.assertEqual(chunk1.data['mpls:22'],self.chunkfoo_1.data['mpls:22'])

    def test_init_tab(self):
        tab = Tab(self.chunkfoo_0,Chunk_position.FIRST)

        self.assertEqual(tab,self.init_tab)

    def test_merge_tab(self):
        chunk10 = load_chunk("0","data/pcQux.dat")
        chunk11 = load_chunk("1","data/pcQux.dat")
        tab = Tab(self.chunkfoo_0,Chunk_position.FIRST)
        tab.add_chunk(self.chunkfoo_1,Chunk_position.FIRST)
        tab.add_chunk(chunk10,Chunk_position.LAST)
        tab.add_chunk(chunk11,Chunk_position.LAST)

        self.assertEqual(tab,self.merged_tab)

    def test_add_intermediate(self):
        chunk10 = load_chunk("0","data/pcQux.dat")
        chunk11 = load_chunk("1","data/pcQux.dat")
        chunk21 = load_chunk("0","data/pcBar.dat")
        chunk22 = load_chunk("1","data/pcBar.dat")
        tab = Tab(self.chunkfoo_0,Chunk_position.FIRST)
        tab.add_chunk(self.chunkfoo_1,Chunk_position.FIRST)
        tab.add_chunk(chunk21,Chunk_position.INTERMEDIATE)
        tab.add_chunk(chunk22,Chunk_position.INTERMEDIATE)
        tab.add_chunk(chunk10,Chunk_position.LAST)
        tab.add_chunk(chunk11,Chunk_position.LAST)

        self.assertEqual(tab,self.full_tab)

    def test_load_files(self):
        chunk10 = load_chunk("0","data/pcQux.dat")
        chunk11 = load_chunk("1","data/pcQux.dat")
        chunk21 = load_chunk("0","data/pcBar.dat")
        chunk22 = load_chunk("1","data/pcBar.dat")
        tab = Tab(self.chunkfoo_0,Chunk_position.FIRST)
        tab.add_chunk(self.chunkfoo_1,Chunk_position.FIRST)
        tab.add_chunk(chunk10,Chunk_position.LAST)
        tab.add_chunk(chunk11,Chunk_position.LAST)
        tab.add_chunk(chunk21,Chunk_position.INTERMEDIATE)
        tab.add_chunk(chunk22,Chunk_position.INTERMEDIATE)
        direct_loaded = load_tab(["data/pcFoo.dat","data/pcQux.dat","data/pcBar.dat"],["0","1"])

        self.assertEqual(direct_loaded,tab)

    def test_jitter_stats(self):
        calculated = GlobalStats(self.tab_for_stats)

        self.assertEqual(calculated.flows_stats["mpls:22"].e2e.jit_stats,self.mpls22_stats.jit_stats)

    def test_delays_stats(self):
        calculated = GlobalStats(self.tab_for_stats)
        self.assertEqual(calculated.flows_stats["mpls:22"].e2e.del_stats,self.mpls22_stats.del_stats)

    def test_multi_stats_jitter(self):
        calculated = GlobalStats(self.tab_for_stats)
        self.assertEqual(calculated.flows_stats["mpls:22"].e2e.jit_stats,self.mpls22_stats.jit_stats)

    def test_multi_stats_delay(self):
        calculated = GlobalStats(self.tab_for_stats)
        self.assertEqual(calculated.flows_stats["mpls:22"].segs[0][1].del_stats,self.mpls22_multistats.segs[0][1].del_stats)

    def test_multi_losses(self):
        calculated = GlobalStats(self.tab_for_l_stats)

        self.assertEqual(calculated.flows_stats["mpls:22"].segs[0][1].loss_stats,\
                self.mpls22_l_multistats.segs[0][1].loss_stats)
        self.assertEqual(calculated.flows_stats["mpls:22"].segs[1][1].loss_stats,\
                self.mpls22_l_multistats.segs[1][1].loss_stats)

    def test_e2e_capacities(self):
        calculated = GlobalStats(self.tab_for_stats)
        self.assertEqual(self.mpls22_stats.bw_stats,\
                calculated.flows_stats["mpls:22"].e2e.bw_stats)

    def test_hop_hy_hop_capacities(self):
        calculated = GlobalStats(self.tab_for_stats)

        self.assertEqual(self.mpls22_stats.bw_stats,\
                calculated.flows_stats["mpls:22"].segs[0][1].bw_stats)

    def setUp(self):
            self.chunk00_data = {
                    "mpls:22":
                    OrderedDict(
                    [
                     ["8",[2.2,10]],
                     ["6",[3.3,20]],
                     ["4",[4.4,30]],
                     ["2",[4.9,40]]
                     ])}
            self.chunkfoo_0 = Chunk("0",[5.0,10.0],self.chunk00_data)

            self.chunk01_data = {
                    "mpls:22":
                    OrderedDict([
                     ["9",12.2],
                     ["7",13.3],
                     ["5",14.4],
                     ["3",14.9]
                            ])
                    }
            self.chunkfoo_1 = Chunk("1",[10,15],self.chunk01_data)
            self.full_tab = Tab()
            self.full_tab.bounds = [5.0,20.0]
            self.full_tab.chunk_id = "0"
            self.f_data ={
                    "mpls:22":
                    OrderedDict([
                     ["8",Packet(2.2,12.2,[11.2],10)],
                     ["6",Packet(3.3,13.3,[12.3],20)],
                     ["4",Packet(4.4,None,None,30)],
                     ["2",Packet(4.9,14.9,[13.9],40)]
                            ])
                        }
            self.full_tab.data = self.f_data

            self.merged_tab = Tab()
            self.merged_tab.bounds = [5,20]
            self.merged_tab.chunk_id = "0"
            self.m_data ={
                    "mpls:22":
                    OrderedDict([
                     ["8",Packet(2.2,12.2,None,10)],
                     ["6",Packet(3.3,13.3,None,20)],
                     ["4",Packet(4.4,None,None,30)],
                     ["2",Packet(4.9,14.9,None,40)]
                            ])
                        }
            self.merged_tab.data = self.m_data
            self.chunk0 = load_chunk(0,"data/pcFoo.dat")
            self.chunk1 = load_chunk(1,"data/pcFoo.dat")
            self.i_data ={
                    "mpls:22":
                    OrderedDict(
                    [
                     ["8",Packet(2.2,None,None,10)],
                     ["6",Packet(3.3,None,None,20)],
                     ["4",Packet(4.4,None,None,30)],
                     ["2",Packet(4.9,None,None,40)]
                            ])
                        }
            self.init_tab = Tab()
            self.init_tab.chunk_id = "0"
            self.init_tab.bounds = [5.0,10.0]
            self.init_tab.data = self.i_data

            self.tab_for_stats = Tab()
            self.tab_for_stats.segs = Seg_manager(["0","1","2"])
            self.tab_for_stats.data =\
            {"mpls:22":
                    OrderedDict([
                    ["4", Packet(4.4 , 9.4 , [11.4],10)],
                    ["2", Packet(4.9 , 14.9 , [13.9],10)] ,
                    ["6", Packet(3.3 , None , [12.3],30)] ,
                    ["8", Packet(2.2 , 12.2 , [11.2],40)] ,
                    ["9", Packet(12.2 , 12.2 , [12.2],50)]
                    ]),
             "vlan100":
                    OrderedDict([
                    ["7", Packet(13.3 , 14.4 , [13.4])],
                    ["5", Packet(14.4 , 14.9 , [13.9])],
                    ["3", Packet(14.9 , 14.9 , [13.9])]
                        ])
                }
            self.tab_for_stats.bounds = [5.0,20.0]
            self.tab_for_stats.chunk_id = "0"
            self.mpls22_stats  = SegStats()
            self.mpls22_stats.jit_stats = JitterStats(-2.5,56.25,-10,5,-2.5)
            self.mpls22_stats.del_stats = DelayStats(6.25,17.1875,0,10,7.5)
            self.mpls22_stats.loss_stats = LossesStats(1,4)
            self.mpls22_stats.bw_stats = BwStats(140,10)
            self.final_stats = GlobalStats()
            self.final_stats.bounds = [5.0,20.0]
            self.final_stats.flows_stats["mpls:22"]=FlowStats()
            self.final_stats.flows_stats["mpls:22"].e2e = self.mpls22_stats
            self.vlan100_delays = np.array([1.1,0.5,0])
            self.vlan100_jitters = np.array([-0.5,-0.6])
            self.vlan100_stats = FlowStats()
            self.vlan100_stats.jit_stats = JitterStats(\
                    np.average(self.vlan100_jitters),\
                    np.var(self.vlan100_jitters),\
                    -0.6, -0.5,
                    np.median(self.vlan100_jitters),\
                   )

            self.mpls22_multistats  = FlowStats()
            self.mpls22_multistats.e2e  = SegStats()
            self.mpls22_multistats.e2e.jit_stats = JitterStats(-2.5,56.25,-10,5,-2.5)
            self.mpls22_multistats.e2e.del_stats = DelayStats(6.25,17.1875,0,10,7.5)
            self.mpls22_multistats.e2e.loss_stats = LossesStats(1,4)
            #SEGMENTS STATS
            self.mpls22_multistats.segs.append(["0:1",SegStats()])
            self.mpls22_multistats.segs[0][1].jit_stats =\
            JitterStats(-1.75,18.1875,-9,2,0)
            self.mpls22_multistats.segs[0][1].del_stats =\
            DelayStats(6.7999999999999998,12.16,0,9,9.0)
            self.mpls22_multistats.segs[0][1].loss_stats = LossesStats(0,5)
            self.final_multistats = GlobalStats()
            self.final_multistats.bounds = [5.0,20.0]
            self.final_multistats.flows_stats["mpls:22"]=self.mpls22_multistats
            #SEGMENTS MANAGER
            self.segs = Seg_manager(["0","1","2","3"])
            #LOSSES SPECIAL CASE
            self.tab_for_l_stats = Tab()
            self.tab_for_l_stats.segs = Seg_manager(["0","1","2"])
            self.tab_for_l_stats.data =\
            {"mpls:22":
                    OrderedDict([
                    ["4", Packet(4.4 , None ,[9.4] )],
                    ["2", Packet(4.9 , None ,[14.9] )] ,
                    ["6", Packet(3.3 , None , [None])] ,
                    ["8", Packet(2.2 , 12.2 , [11.2])] ,
                    ["9", Packet(12.2 , 12.2 , [12.2])]
                    ])
                }
            self.tab_for_l_stats.bounds = [5.0,20.0]
            self.tab_for_l_stats.chunk_id = "0"
            self.mpls22_l_multistats  = FlowStats()
            self.mpls22_l_multistats.e2e  = SegStats()
            self.mpls22_l_multistats.e2e.jit_stats = JitterStats()
            self.mpls22_l_multistats.e2e.del_stats = DelayStats()
            self.mpls22_l_multistats.e2e.loss_stats = LossesStats(3,2)
            #SEGMENTS STATS
            self.mpls22_l_multistats.segs.append(["0:1",SegStats()])
            self.mpls22_l_multistats.segs[0][1].jit_stats = JitterStats()
            self.mpls22_l_multistats.segs[0][1].del_stats = DelayStats()
            self.mpls22_l_multistats.segs[0][1].loss_stats = LossesStats(1,4)
            self.mpls22_l_multistats.segs.append(["1:2",SegStats()])
            self.mpls22_l_multistats.segs[1][1].jit_stats = JitterStats()
            self.mpls22_l_multistats.segs[1][1].del_stats = DelayStats()
            self.mpls22_l_multistats.segs[1][1].loss_stats = LossesStats(2,2)

class TestAggregator(unittest.TestCase):
    def test_init(self):
        agg = Aggregator()
        self.assertEqual(agg.has_nothing_to_do(),True)

    def test_add(self):
        agg = Aggregator(["MA4","MA3","MA5"])
        agg.add(0,2)
        agg.add(1,1)
        agg.add(2,0)
        agg.add(3,2)
        self.assertEqual(self.good_agg,agg)
        self.assertRaises(ValueError,agg.add,1,3)

    def test_must_load(self):
        agg = Aggregator(["MA4","MA3","MA5"])
        a = agg.add(0,1)
        agg.add(0,2)
        b = agg.add(0,0)
        self.assertEqual(a, Action.IDLE)
        self.assertEqual(b, Action.LOAD)

    def test_load_first(self):
        agg = Aggregator(["Foo","Bar","Qux"])
        agg.update_files_meta(["data/pcFoo.dat","data/pcBar.dat","data/pcQux.dat"])
        self.assertEqual(self.agg_for_files,agg)

    def test_chunks_meta(self):
        m_data= ChunksMetadata(3)
        self.assertEqual(m_data.width,3)
        self.assertFalse(m_data.has(0,0))
        self.assertFalse(m_data.has(1,1))
        self.assertRaises(ValueError,m_data.has,1,3)

    #def test_remove_useless_line(self):
    #    agg = Aggregator(["MA4","MA3","MA5"])
    #    agg.add(0,2)
    #    agg.add(0,1)
    #    agg.add(0,0)
    #    i = agg.get_next_chunk_to_load_id()
    #    self.assertEqual(i,0)
    #    self.assertEqual(len(agg.metadata.lines),0)

    def test_line(self):
        l = Line(0,3)
        self.assertEqual(len(l.values),3)
        self.assertFalse(l.values[0])

    def test_line_complete(self):
        l = Line(0,3)
        l.set_true_at(0)
        self.assertFalse(l.is_complete())
        l.set_true_at(1)
        l.set_true_at(2)
        self.assertTrue(l.is_complete())

    def test_agg_fill_meta(self):
        files1 =\
                ["data/test_agg/pc1_agg1.dat","data/test_agg/pc1_agg1.dat","data/test_agg/pc1_agg1.dat"]
        files2 =\
                ["data/test_agg/pc1_agg2.dat","data/test_agg/pc1_agg2.dat","data/test_agg/pc1_agg2.dat"]
        agg = Aggregator(["pc1","pc2","pc3"])
        agg.update_files_meta(files1)
        self.assertEqual(len(agg.metadata.lines),4)
        agg.update_files_meta(files2)
        self.assertEqual(len(agg.metadata.lines),7)

    def test_get_id_alters_agg(self):
        files1 =\
                ["data/test_agg/pc1_agg1.dat","data/test_agg/pc2_agg1.dat","data/test_agg/pc3_agg1.dat"]
        files2 =\
                ["data/test_agg/pc1_agg2.dat","data/test_agg/pc2_agg2.dat","data/test_agg/pc3_agg2.dat"]
        agg = Aggregator(["pc1","pc2","pc3"])
        agg.update_files_meta(files1)
        self.assertEqual(len(agg.metadata.lines),4)
        agg.update_files_meta(files2)
        self.assertEqual(len(agg.metadata.lines),7)
        for i in range(4):
            a = agg.get_next_chunk_to_load_id()
        self.assertEqual(agg.metadata.lines[0].already_loaded, True)
        self.assertEqual(agg.metadata.lines[2].already_loaded, False)
        self.assertEqual(agg.metadata.lines[5].already_loaded, False)
        self.assertEqual(agg.metadata.lines[6].already_loaded, False)


    def setUp(self):
        self.good_agg = Aggregator(["MA4","MA3","MA5"])
        self.good_agg.metadata = ChunksMetadata(3,4)
        self.good_agg.metadata.n_col = 3
        self.good_agg.metadata.lines[0].values[2] = True
        self.good_agg.metadata.lines[1].values[1] = True
        self.good_agg.metadata.lines[2].values[0] = True
        self.good_agg.metadata.lines[3].values[2] = True

        self.agg_for_files = Aggregator(["Foo","Bar","Qux"])
        self.agg_for_files.metadata = ChunksMetadata(3,2)
        self.agg_for_files.metadata.n_col = 3
        self.agg_for_files.metadata.lines[0].index = 0
        self.agg_for_files.metadata.lines[0].values[0] = True
        self.agg_for_files.metadata.lines[0].values[1] = True
        self.agg_for_files.metadata.lines[0].values[2] = True
        self.agg_for_files.metadata.lines[1].index = 1
        self.agg_for_files.metadata.lines[1].values[0] = True
        self.agg_for_files.metadata.lines[1].values[1] = True
        self.agg_for_files.metadata.lines[1].values[2] = True

class TestTsAnalyzer(unittest.TestCase):

    def test_packet_right_order(self):
        p1 = Packet(4,1,[3,2])
        p2 = Packet(1,4,[2,3])
        right_order = [3,2,1,0]

        self.assertEqual(right_order,p1.right_order())

    def test_swap_index(self):
        p1 = Packet(1,4,[2,3])
        p2 = Packet(1,4,[])

        self.assertEqual(1,p1.swap_index(0))
        self.assertEqual(2,p1.swap_index(1))
        self.assertEqual(3,p1.swap_index(2))
        self.assertEqual(4,p1.swap_index(3))
        self.assertEqual(1,p2.swap_index(0))
        self.assertEqual(4,p2.swap_index(1))
        self.assertRaises(Exception,p2.swap_index,2)

    def test_p_sorting(self):
        p1 = Packet(4,1,[3,2])
        p1_sorted = Packet(1,4,[2,3])
        p2 = Packet(1,4,[3,2])

        self.assertEqual(p1_sorted,p1.swap([3,2,1,0]))
        #self.assertIsNone(p2.swap([3,2,1,0]))


    def test_analyze(self):
        new_orders = get_swap_instructions(self.unsorted_tab)

        self.assertEqual(new_orders,self.instructions)

    def test_swapper(self):
        new_tab = sort_packets_ts(self.unsorted_tab)
        self.assertEqual(self.sorted_tab,new_tab)

    def setUp(self):
        self.unsorted_tab = Tab()
        self.unsorted_tab.segs = Seg_manager(["0","1","2"])
        self.unsorted_tab.data =\
        {
        #Needs no change
        "mpls:22":
                OrderedDict([
                ["4", Packet(4.4 , 11.4 , [9.4],10)],
                ["2", Packet(4.9 , 14.9 , [13.9],10)] ,
                ]),
         #Reverse order in each line : needs sorting
         "vlan100":
                OrderedDict([
                ["7", Packet(4 ,1 , [3,2])],
                ["5", Packet(6 ,3 , [5,4])],
                ["3", Packet(8 ,5 , [7,6])]
                    ]),
         #Reverse order in first line but not following : deleted
         "vlan200":
                OrderedDict([
                ["7", Packet(4 ,1 , [3,2])],
                ["5", Packet(4 ,1 , [3,2])],
                ["3", Packet(14.9 , 15.0 , [14.5,14.3])]
                    ]),
            }
        self.unsorted_tab.bounds = [5.0,20.0]
        self.unsorted_tab.chunk_id = "0"

        #self.vlan100_swap_instructions = SwapInstructions()
        #self.vlan100_swap_instructions.before =

        self.instructions = SwapInstructions(
        {
                "mpls:22": [0,1,2],
                "vlan100": [3,2,1,0],
                "vlan200": [3,2,1,0]
                })

        self.sorted_tab = Tab()
        self.sorted_tab.segs = Seg_manager(["0","1","2"])
        self.sorted_tab.data =\
        {
        #Untouched
        "mpls:22":
                OrderedDict([
                ["4", Packet(4.4 , 11.4 , [9.4],10)],
                ["2", Packet(4.9 , 14.9 , [13.9],10)] ,
                ]),
         #Each line reversed
         "vlan100":
                OrderedDict([
                ["7", Packet(1 ,4 , [2,3])],
                ["5", Packet(3 ,6 , [4,5])],
                ["3", Packet(5 ,8 , [6,7])]
                    ]),
         #Deleted
         "vlan200":
                OrderedDict([
                ["7", Packet(1 ,4 , [2,3])],
                ["5", Packet(1 ,4 , [2,3])],
                ["3", Packet(15.0 ,14.9 , [14.3,14.5])]
                    ]),
            }
        self.sorted_tab.bounds = [5.0,20.0]
        self.sorted_tab.chunk_id = "0"


if __name__ == '__main__':
    unittest.main()
