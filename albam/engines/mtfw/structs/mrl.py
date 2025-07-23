# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Mrl(ReadWriteKaitaiStruct):

    class MaterialType(IntEnum):
        type_n_draw__material_null = 139777156
        type_n_draw__dd_material_std = 480978014
        type_n_draw__dd_material_inner = 651803228
        type_n_draw__dd_material_water = 819701071
        type_n_draw__material_std = 1605430244
        type_n_draw__material_std_est = 2099982771

    class TextureType(IntEnum):
        type_r_texture = 606035435
        type_r_render_target_texture = 2013850128

    class CmdType(IntEnum):
        set_flag = 0
        set_constant_buffer = 1
        set_sampler_state = 2
        set_texture = 3
        set_unk = 4

    class ShaderObjectHash(IntEnum):
        flinearcolor = 144
        getbiasedviewposition = 543
        fbaselightscattering = 1145
        bsaddrwrite = 2367
        ps_ambientshadow = 3207
        fmrtnormalcombinear = 4069
        fuvextendmapsecondary = 5061
        fgpuparticletonemapdefault = 5927
        fappoutline = 5987
        cbprimitiveparticletess = 6540
        fheightfogmodelvtf = 6720
        calcfog = 6726
        fprojectiontexturecolor = 6902
        cbfilteredgeantialiasing = 7114
        fmirageclampnearfar = 7511
        fswingjointsupportdisable = 7907
        bsbwrite = 7949
        fshadowfilterpcf2x2comp = 8074
        cbskyfog = 8250
        fmaterialstdreflectiontypedefault2mask = 8856
        fsystemcachedecodecopy = 8980
        fpervertexshadowfilter4x4 = 9112
        spotlighttexture = 9694
        cbwater = 10433
        fmaterialstdreflectiontypelightrim = 10882
        iamirage = 10916
        fmaterialstdreflectiontyperim2 = 11427
        ia_nonskin_bl_la = 11644
        tambientshadowmap = 11996
        ps_tattoo = 12198
        makedirectionfromuv = 12964
        ssborderpoint = 13386
        fvdgetmask = 13446
        fbrdfgrassdefault = 14661
        tvtxdispmask = 14784
        fprimitive2dvirtualscreenletterbox = 15191
        ia_filter0 = 15302
        sbtexcoordtoposition = 15360
        fgrasscossinfromangle = 16455
        vs_materialdummyedge = 16512
        fguicalcuvclamp = 16628
        fdynamiclight2 = 17463
        vs_filter = 17758
        cbprimitivemetadatafresnel = 18433
        fencodersmparameter = 19835
        bsadd = 20370
        cboutlineex = 20690
        vs_infparticle = 20872
        dsprimzwritestenciltestneq = 21054
        ffilteroutlinethick = 21193
        tdistortionblendmap = 21217
        tmirror = 21242
        fprimitivetonemapnone = 21374
        bsblendadddestcolorrgb = 21912
        ffog = 21987
        tcubemap = 23103
        fuvdetailnormalmap = 23733
        vs_gpuparticle2 = 23803
        fdebugviewpixeltangentnormalmap = 23969
        calctexcoord = 24125
        tthinmap = 24362
        tfiltertempmap2 = 24589
        light_param = 24677
        tdofmap = 25075
        filtercascadevlsm = 26314
        tssaonormalmap = 26412
        iatetradeform = 26946
        ia_simwater_for_view_vs_input = 27265
        cbguiglobal = 27312
        cbdynamiclightingdl = 27762
        ia_nonskin_b = 27824
        fprimitivescenesamplerrefractzblur = 27973
        sky_out = 27979
        tnormalburnmap = 28177
        bsrevsubblendalpha = 28695
        fdeferredlightingencodeparametermrt = 29330
        fprimitive2dcalctexcoordtexel = 30154
        vs_materialstdlite = 30172
        fmiragesamplescenerefractionmap = 30195
        ia_skin_velocity_edge = 30560
        cbshadowfrustum = 30873
        fswingdefaultviewi = 30894
        ia_nonskin_tbc = 31124
        finfparticlerandomizepos = 32664
        primitiveconsths = 32914
        fsamplecount18 = 33067
        ps_bloomconeblur = 33587
        dsguistencilwrite = 34237
        treflectiveshadowmap = 34288
        dynamicedit_output = 34655
        tprocedural2d2 = 35364
        fblendfogprimalpha = 35487
        fskinning8weightbranch = 35989
        ps_deferredlighting_gbufferreduction = 36533
        fshadowreceiveattnviewdistance = 36716
        tocclusiondepth = 36941
        vs_gsdoffilter = 36983
        fimageblendexclusion = 37276
        getdeveloptexcubeface = 37581
        bsaadd = 37741
        falphatestless = 37803
        ps_deferredlighting_bilateralblurv_size16 = 37892
        dsguiztestwritestencilapply = 37966
        ia_grass = 38881
        fskinningpf2weight = 39094
        fshadowisoutofrange2 = 39123
        rsmeshbias8 = 39599
        ps_tangentfilter_blur8 = 39691
        fxaafilter = 40287
        vs_textureblend = 42312
        fprocedural1d4e1 = 42976
        tambientmaskmap = 43040
        max4 = 43361
        fprocedural4e = 43415
        tsoftbodytexdepthnorm7 = 43443
        fmaterialstdreflectiontypeproc = 43865
        fskinningpf4weight = 44428
        tbasemap = 44852
        fdeferredlightinggetlightingresult = 44913
        cbmark = 45028
        vs_cubicblend = 45251
        ffiltercolorcorrect = 45399
        bsrevsubalphargb = 45475
        fshadowreceivecascadessmrt = 45492
        fshadowreceivecascadelsmrt = 45543
        fprimitivealphatocolor = 45934
        dsprimzwritestenciltesteq = 46299
        vs_builder = 46324
        fprimitivecalcnormalmapmask = 46342
        cbskystar = 46392
        foutlinedetectordepth = 46527
        calcparticleintensity = 47210
        sbboxconstraint = 47276
        tlutshininess = 47512
        tmaterialdebug = 47684
        ssparallaxheightmap = 47710
        fdebugviewvertexbonemap = 47847
        fprimitivemodelscenesamplerrefract = 48089
        calcfluctuation = 48372
        cbprimitiveview = 48585
        ps_occlusinquery_basic = 48595
        twaterdetail2 = 48798
        fmaterialstdspecularmaskexmodulateextend = 48824
        focclusionambient = 48841
        fshaderattributesvtf = 49152
        getatmospheredepth = 50330
        ffilteredgeantialiasinggetdepth = 50967
        fskinningpf8weight = 51192
        iaskinbridge4wt = 52072
        dynamicedit_input = 52163
        ia_grass_hicomp = 52654
        fchannelb = 52847
        cbsbextrapolation = 54006
        cbssaoffilterintensity = 54096
        ps_deferredlighting_lightvolume_nolighting_lightgroup = 54156
        ps_grassfinalcombiner = 54340
        iasoftbodyvertexps3 = 54499
        bsshadowrecvtransparentgroup1 = 54662
        freflectglobalcubemap = 54716
        fdiffusethin = 55623
        iaskintbn2wt = 55784
        fprocedural2d4e1 = 56624
        fdynamiceditmapscalingenable = 56658
        ps_grass = 56754
        fxaa3hq = 56915
        fshadowfilterpcf4x4comp = 57104
        fbilateralfilterv = 57371
        tadhesion = 57422
        fbumpdetailnormalmap2 = 57591
        falphatestgreaterequal = 57971
        cbfisheyefilter = 58080
        tspotlighttexture0 = 58084
        fswingupdateyaxis = 58206
        fgodraysdirection = 58227
        foutputencodesrgbrcrgb = 59941
        bsshadowrecvsolidgroup0 = 60114
        tspecularmap = 60699
        cblightscattering = 61293
        bsblendblendalpha = 61595
        fprimitivescenesamplerdistortion = 61598
        creatematerialcontextexest = 62717
        water_ripple_output = 62802
        twatercaustics = 62858
        ia_instancing = 62968
        fvertexdisplacementdirv = 64190
        swing_input = 64299
        cbviewprojectionpf = 65324
        fwinddirection = 66373
        cbbloomfilter = 66408
        fmaterialstdvertexocclusiondefault = 66503
        tprocedural1d3 = 66795
        ia_nonskin_tbn = 66857
        fvariancemakemiplevelcube = 66870
        tmaterialtoonsm = 66975
        rsmesh = 67791
        ia_primitive_polyline = 68612
        toonshadowmaskuber = 68871
        falphatestlessequal = 68931
        tmaterialdummy = 69596
        iagrassoutsourcing = 69685
        fcalcprimarycolorstdlitealphavertex = 70003
        foutputencode = 70071
        calcpos = 70137
        vs_avgloginit = 70181
        fimageblendsoftlight = 70335
        fwatershadowface = 70858
        cbambient = 70953
        ssenvmaplodbias3 = 71358
        fgpuparticlesample = 71506
        fmaterialstdreflectiontyperim = 71806
        fperpixellightingtoonlmtps = 71822
        cbshadowcastoption = 71877
        fbokehcalculation = 72045
        cbcolormodifieropticalcamouflage = 72328
        ssclamplinear = 73134
        cbprimitiveparallaxtess = 73938
        easein = 73954
        ps_deferredlighting_indirectlighting = 74734
        fworldcoordinatefromtexture = 74743
        ianonskintbla = 75091
        fskinningpfnone = 75174
        fgrassfade = 75758
        cbtvnoisefilter = 75801
        fbokehmaskvalue = 75823
        fdynamiclocalwind3 = 75868
        fguicalccoloralphamaskwrite = 75952
        cbshadowlight = 77035
        ffiltergodraysthreshold3dboundmaskweightzero = 77037
        ps_materialoutline = 77345
        fparaboloidprojection = 77764
        fmarkloopline = 77835
        ssshadowvariance3 = 77879
        ffiltermotionblur8 = 78132
        fimageblend = 78512
        tdispersionmap = 79215
        timageplanefilter = 79344
        iaskystar = 79941
        foutlinedetector2 = 80011
        dsfilterstencilequal = 80037
        ffiltercolorcorrectdepth = 80046
        fssaofilterdepthdownscale = 80086
        fmaterialstdspecularmaskextend = 80347
        bsmrtwrite1110 = 80353
        ffiltercolorcorrectvolumesrgbblend = 80502
        ps_deferredlighting_gbufferpassest = 80907
        bsblendfactoralpha = 80963
        fprimitivelevelcorrectionlinear = 81095
        fddmaterialalbedo = 81695
        fprocedural3e = 81744
        tpointlighttexture1 = 81868
        system_mrt3 = 81973
        iagpupolylineparticle = 82067
        builder_ps_input = 82223
        fuvunique = 82449
        ssprimocclusionmap = 83195
        fskymapbeginendrayleigh = 84183
        calcwaveheight = 85176
        iaskintb4wt = 85312
        freconstructworldposition = 86574
        tvertextangentmap = 86578
        iagrassoutsourcingf32 = 86843
        cbvertexdisplacement = 87065
        fbrdfanisotropicphong = 88108
        fdynamiclightdl2 = 88166
        sbsolveedgeconst2ps = 89185
        fswingadjustposition = 89359
        ps_systemdepthcopy = 89512
        skinning_input = 89537
        vs_water = 89884
        bsmrtwrite0101 = 89939
        ffilteroutlinesample = 90593
        bsambientmaskalphagroup1 = 91128
        fdevelopdecode_rgbn = 91415
        fwaterbubbletexturecoordinate = 91475
        vs_ambientshadow = 91491
        bssubbwrite = 91612
        gs_gpuparticle = 92283
        cbmaterialsssblend = 92535
        ttransparencymap = 92554
        fsamplecount21 = 92748
        cbmaterialstd = 92763
        ffilteroutlinedetector = 92939
        fdynamiceditmaplying = 93168
        ffogdistance = 93186
        fwaterrippledisable = 93424
        cbwaterwave = 93743
        tburnemissionmap = 94217
        tsoftbodysrctex7 = 94682
        ftransparency = 94685
        tgrassshadowdummy = 94963
        ffiltergodrayso2p = 95016
        cbprimitivemodeldistortion = 95103
        ffixedcoordinate = 95400
        foutputencodenone = 95756
        fprojectiontexturecolorb = 96143
        cbsoftbodyquad = 96171
        fswingadjustpositiondisable = 96551
        fvertexdisplacementdiruv = 96627
        foutlinesample = 96744
        cbfilter = 96832
        fprimitive2dcalctexcoord = 96878
        ps_systemdepthvmax = 97037
        ia_softbody_vertex = 97076
        ffilterdeferredrendering = 97755
        tshadowcast = 97813
        cbblendfactor = 98214
        cbjointmatrixpf = 98454
        fdistortionrefractmask = 98554
        tspecularblendmap = 98767
        focclusionfactorfilter = 98793
        fprimitivecalcvolumeblend = 99163
        fchromaticaberrationfilterdownsample = 99455
        tnormalmaskmap = 100343
        fambientmask = 100520
        fprimitivemodelsmoothalphavertexnormalinverse = 101281
        fdissolvepatterntexture = 102314
        ldnormalunpackf32 = 102694
        fgpuparticlecalcposlineparticle = 103088
        ffilterhazedepth = 104037
        fcuboidlightd = 104086
        fshadowreceiveattndistancefade = 104717
        frsmgetindirectlighting = 104731
        ffogdistancecolortable = 106045
        flightmaskshadowmultirt1 = 106155
        cbshadowreceive2 = 106302
        fprimitivecalcvolumeblendpsdepthvolume = 106528
        fdeferredlightingdecodeparameter = 106679
        fshadowreceiveattn3 = 106796
        fbrdf = 106951
        fdithering = 107181
        vs_deferredlighting_lightvolume = 107205
        fmaterialstdreflectiontypeextend2 = 107351
        ffresnel = 107649
        fradialbluralphaocclusion = 108024
        iaswing = 108193
        fskyfinalcombiner = 108517
        toonshadowmaskdisable = 108737
        fprocedural2d3e3 = 109209
        ia_deferred_lighting_light_volume = 110073
        ialightshaftinput = 110437
        fskycorrecthorizon = 110466
        fdeferredlightingdecodeparameterhalflambert = 110566
        fheightfogmodel = 111142
        fmiragemodcolordebug = 111432
        fshadowreceivecascadessmlite = 111452
        ds_primitivetessellate = 112362
        calcscattering = 112406
        ps_deferredlighting_bilateralblurh_size16 = 112413
        getintensitysingleface = 112507
        ftex2anisotropicphongspecularmodel = 112619
        getbubblecolor = 112777
        grass_input = 112921
        fgrassbillboardtangent = 113783
        ps_dummypicker3 = 113805
        finfparticlevsalphaclip = 114661
        ia_softbody_quad = 114958
        ia_grass_lowest = 115904
        dsdeferredlightingzteststenciltest = 115999
        ps_heatdepth = 116298
        adhesion_output = 116450
        cbmiplevel = 116586
        falbedo = 116590
        tshaderattributes = 117095
        thairshiftmap = 117546
        fimageblendoverlay = 117888
        cbambientmask = 118367
        fdevelopdecode_b = 118525
        bsblendmaxalphargb = 118557
        fcolormaskalbedomap = 118632
        ps_deferredlighting_lightvolume = 118819
        fprocedural1d3e3 = 118857
        ffiltertexcoord = 119499
        flightmaskrtsolid1 = 119820
        vs_skystarryskycolor = 119826
        cbcolorcorrectfilter = 121343
        setuplightbalance = 122184
        vs_dof_input = 122829
        ps_deferredlighting_lightvolume_nolighting = 123234
        vs_fxaa3 = 123358
        tocclusionmap = 123937
        flightingdeferredlighting = 124264
        rsmeshbias5 = 124434
        ps_grassdummy = 124738
        vs_occlusinquery_basic = 124755
        vs_bloomconeblur = 125655
        fmaterialstdspecularmaskexvertexcolorg = 125999
        cbhermitecurve = 126015
        fgrassillumination = 127087
        cbspecularblend = 127174
        sb_psmrtout3 = 127212
        fshadowmultireceivespotvsmrt = 128466
        cbgodraysiterator = 128984
        ps_grassshadowreceivetransparent = 130330
        ps_modelnormalize = 130438
        fsamplecount15 = 130454
        fprimitivepsocclusiondefault = 131048
        getcloudscatter = 131064
        iaswing2highprecision = 131102
        fvduvtransformoffset = 131626
        bsblendadd = 132386
        ianonskinbc = 133078
        toonvertexcoloruber = 133121
        ianonskinbla = 133167
        ssvariance = 133224
        fshadowmultireceivepoint = 133232
        ps_proceduraltexturesnorm = 133534
        ssshininessmap = 133929
        fldtexturesampler3wprevxbox = 134625
        fdeferredlightinglightvolumelightmasktransparentquartersize = 134724
        fprimitivesamplealphamap = 135174
        cbrsmindirectlighting = 135186
        ffresnellegacy = 135296
        ia_primitive_cloud = 135753
        sbisccalcft = 135799
        fcuboidlights = 136017
        ps_deferredlighting_bilateralblurv_size8 = 136217
        cbtextureblend = 136544
        ffiltergodraysblend = 136558
        cbgrassmaterial = 136705
        forennayarmodel = 136813
        fvariancefiltercubev = 137192
        ps_infparticle = 137790
        fmaterialstdreflectiontypeextend2mask = 138125
        rsguiscissorenable = 139008
        fblendratenormalmap = 139313
        fprimitivecalcntbparticle = 139772
        fspotlightr = 140077
        getcrosspoint = 140305
        mirror_output = 140497
        tlightaccumulationtexture0 = 140726
        tnormalmap = 140896
        ttextureblendsource0 = 140924
        fmaterialstdspecularcolortypeproc = 140949
        ps_vignettegather = 140955
        cbvertexdisplacement3 = 141442
        fdeferredlightingencodeoutput = 141464
        ia_lightshaft_input = 141759
        ps_systemfillstencilrouting = 141959
        toonshadowmaskenable = 143130
        ffilteroutlineblur = 143141
        ffiltermotionblurneighbormax = 143402
        ftonemapexposure = 143437
        fmaterialstdspecularmaskexaddproc = 143686
        tindirectlighting = 143935
        fcuboidlightb = 144291
        vs_imageplanefilter = 144403
        unpacku8u8 = 144445
        sbcreatedepthnormfrontps = 144513
        fprocedural1d1e2 = 144561
        tbloomfilter = 145148
        fguicalcuvalphamaskon = 145404
        fuvnormalmap = 145634
        flighting = 145808
        trayleighdepthmap = 146044
        fbokehmaskdither = 146275
        cbhazefilter = 146335
        bsblendalpha = 146351
        cbmirror = 146967
        fdeferredlightinglightvolumelightmasksolid0 = 147307
        ps_reflectiveshadowmapest = 147334
        fbeckmannmodel = 147389
        finstancingenable = 147472
        fdeferredlightingencodeparameter = 147634
        vs_tangentfilter = 148079
        rsmeshbias3 = 148263
        fspecularmap = 148864
        cbuvrotationoffset = 149486
        vs_shadowreceive = 149918
        fupperposydiscardcolormodifier = 149955
        ps_skystarryskycolor = 149959
        fprocedural2d1e2 = 151137
        fuvalbedoblendmap = 151397
        fdiffuselightmap = 152081
        strandspecular = 152562
        fbokehinflatemask = 152572
        dsdeferredlightingzteststencilwritedepthfail = 152574
        cblightgroup = 152644
        cbsoftbodysim = 152653
        ps_deferredlighting_lightvolume_nolighting_mrt = 153018
        softbody_input = 153142
        ps_deferredlighting_bilinearupsampling = 153567
        bsblendblendalphargb = 153595
        fsamplecount13 = 153763
        dual_paraboloid_output = 153827
        fshadowreceivert3 = 154114
        ps_deferredlighting_lightvolume_mrt = 154217
        foutlinecompositemultiblend = 154248
        fprimitivedepthcomparisonenable = 154631
        ssnormalmap = 154742
        fmaterialstdspecularmaskexaddextend = 154822
        fshadowreceivesmoothcascadessm = 155355
        fdistancefog = 155419
        tmaterialstd = 155599
        fprimitivecalcposparticlent = 155783
        falbedotextureblendmap = 155798
        ps_materialoutline2 = 155888
        fgrassposition = 156510
        ps_develop = 156885
        fwaterbubblemask = 157688
        fwaterwposprot = 158478
        ssshadowdepth = 158524
        ftonemaplinear = 159379
        ffiltercolorcorrectvolumeinterpolatehq = 160510
        vs_grassshadowdummy = 160528
        dsztestwriteback = 160750
        vs_deferredlighting_lightvolumerectangle = 160942
        bsambientmaskgroup3 = 160997
        fgrassdiffuse = 161016
        fgpuparticlefogvsblend = 161285
        fmiragesectcombiner = 161520
        fshadowfiltervlsm = 161824
        fgpuparticlecalcpos = 161848
        bsaddawrite = 162058
        ffiltergodraysthresholdwithz = 162464
        fuvalbedoblend2map = 162554
        fdynamiceditmapfadeenable = 163020
        fshadowfilter3 = 164039
        iaprimitivent = 164229
        sspoint = 164559
        tvertexnormalmap = 164585
        mrtoutput = 165397
        vs_systemdownsample16 = 166284
        bsrgbwrite = 166858
        occlusion_query_vs_output = 167064
        fdynamiclocalwind5 = 167273
        fwaterunitprot = 167281
        cbsoftbodycollision = 167631
        sbpositiontotexcoord = 167772
        fuvproj = 167775
        fdevelopdecode_rgb = 168584
        calczoffset2d = 169581
        rsscissormesh = 170115
        tvertexpositionmap = 170206
        fbumpdetailmasknormalmap = 170423
        ffiltermotionblurvelocityblend = 170588
        tpointlighttexture7 = 170745
        fshadowreceivesmoothcascadessmrtlite = 171633
        tgrassalbedomap = 171811
        tyuvdecoderv = 172381
        ia_skin_tbnla_1wt = 172961
        fworldcoordinatetransformed = 173494
        cblightmask = 173986
        ia_nonskin_tbna = 174191
        fprimitivecalcintensity = 174198
        toonvertexcolorenable = 174304
        cubemap_variance_filter_output = 174404
        rsmeshcf = 174849
        fbrdfmetal = 175007
        tssaonarrowmap = 175023
        foutputencodercrgb = 175408
        cbgpuparticlelvcorrection = 175669
        fsystemconverthightmaptoparallaxmap = 176021
        finfparticlecalctexcoordpattern = 176319
        fmaterialstdreflectiontypeextend = 176912
        ssenvmaplodbias5 = 177035
        ffiltermotionblur8median = 177059
        ps_gui_blend = 177577
        flddeformer = 177697
        flddeformerwithprev = 178711
        flightmasktransparent01 = 179339
        fsimwatersimpletexvs = 179763
        fcuboidlight = 180499
        ffogvtfdistancecolortable = 180797
        ps_materialstdest = 181669
        fwrinkledetailnormalmap = 182363
        maskoutlinegeometry = 182461
        foutlinecomposite = 182628
        ffrontfacenormaltwosidedlh = 183077
        fguicalccoloralphamask = 184162
        fsamplecount27 = 184185
        fskymapoutputselect = 184406
        filter_output_16 = 184978
        fgpuparticleintensity = 184989
        fquaterniontomatrix = 185493
        tsoftbodysrctex1 = 185583
        fperpixellightingps = 185835
        fdamagesimplealbedomap = 185878
        fdiffusevertexcolor = 185954
        fgrassuv = 186007
        ffiltercolorfog = 186288
        twater = 186494
        ffiltermotionblur4median = 186839
        fshadowlightfacepoint = 186894
        fprimitivelevelcorrection = 187139
        fscheuermannmodel = 187231
        ps_gsdoffilter = 187329
        vs_out_gui = 187412
        ps_materialconstantlite = 188177
        fdevelopdecode_rgby = 188624
        fcolormodifier = 188656
        fambientshadowdecayuniform = 189206
        ffogdistancetable = 189475
        ffilteredgeantialiasinggetedgeweight = 190042
        fperpixellightingtoonvs = 190170
        fvtxdispgenwave = 190196
        fgrasspervertexlightmask = 190767
        fwindtrianglecurve = 190805
        fbrdf_toon_lite = 191039
        fshadowfilterpoint1 = 191715
        flocalwindpoint = 192312
        cbradialblurfilter = 192448
        twcvtfprevpos1 = 192494
        ps_systemclear = 192691
        ffogvtfdistancecolortableest = 192965
        fshadowreceivespotvsmrt = 193111
        ia_nonskin_ba = 193254
        cbprimitivetessellation = 193342
        cbsystemnormalslope = 193497
        iaskinotb_4wt_4m = 193884
        forennayarrgbmodel = 194097
        fgrassuvswitchdisable = 194169
        ps_proceduraltextureunorm = 195646
        bsblendrevsub = 195722
        fdynamiclightdl4 = 195923
        sbapplyworldoffsetps = 196090
        ps_ssaomakenormal = 196756
        vs_mirror = 196873
        fdegamma = 197395
        hs_primitivetessellate = 197610
        dszteststencilwrite = 197905
        ps_skymoonbody = 198216
        tguialphamap = 198567
        fprimitivesamplebasemap = 199103
        fsamplecount32 = 199351
        tsoftbodytexdepthnorm1 = 199814
        iafilter0 = 199995
        fgpuparticlefogvs = 200559
        ffogdistancecolortableest = 201044
        fshadowreceivespotvsm = 201657
        fgpuparticlecalcdepthblendnone = 201800
        texture_blend_output = 202357
        ia_nonskin_tb = 202379
        tfilter = 202413
        cbguistaticcolor = 202756
        tmiescattermap = 203219
        vs_ssaomakeocclusionmap = 203253
        ia_skin_bridge_4wt = 203300
        ffiltercolorcorrectvolumesrgb = 203475
        fmaterialstdreflectiontypeproc2mask = 203789
        material_output = 204133
        vs_variancefilter = 204854
        ps_shadowreceive = 204922
        tdistortionmap = 205061
        foutputtexcoord = 205384
        frimaddbase = 206096
        cbvertexdispuv = 206143
        hs_pntrianglesconstant = 206405
        cbswing2weight = 206591
        dsdeferredlightingzwritestenciltestrouted = 206977
        fprimitivesamplebasemaplin = 207024
        material_ph_output = 207441
        fswingbillboardrotation = 207587
        bsbawrite = 207658
        fspotlightbr = 208095
        vs_cubicblur = 209208
        fshininess2 = 209491
        ffilterlightscatteringadd = 210198
        bsmrtwrite0001 = 210276
        fdissolvedither = 210370
        cbshadowreceivermode = 210519
        fuvlightmap = 210743
        ia_sky_star = 210815
        ssspheremap = 211426
        fprimitivemaskmapdefault = 211528
        ia_filter = 211992
        fwatershadowreceivecascadelsm = 212496
        fwatercombiner = 212701
        grass_infomation = 213001
        fuvvertexdisplacement = 213552
        tspheremap = 214004
        fdynamiceditmapfade = 214081
        cbquantcompress = 214932
        tspotlighttexture6 = 214993
        ttangentmap = 215314
        tsssdiffusemap1 = 215794
        fgpuparticlefogpsdefault = 216377
        fgpuparticlevsalphaclip = 216581
        sblodtransps_xbox = 216692
        fquaternioninverse = 217243
        sbnormalunpackf32 = 217706
        fskymapbeginendmie = 217972
        ia_swing2 = 218013
        bsmrtwrite1010 = 218070
        fchannelshininessmap = 218514
        ftattoouvnormalmap = 219110
        ps_deferredlighting_gbufferpassmrt = 219288
        twaterreflection = 219759
        fgpuparticlecalcpospolylineparticle = 220296
        fldtexturesampler3 = 220759
        doadhesioneachlighting = 221057
        fshadowreceivefaceattn = 221409
        fprimitivecalceyedefault = 222162
        fjointmatrixpf = 222377
        bsnvmodelblendalpha = 223032
        tstarryskymap = 223152
        ps_mirage = 223845
        fgpuparticlecalctexcoordpolyline = 224000
        fuvnormalblendmap = 224357
        fgpuparticlevsalphaclipdefault = 224966
        grass_reflection = 225115
        fguicalcposition3d = 225436
        inf_particle_vs_input = 225515
        fspecularsh = 227029
        tdepthmap = 227254
        iabokeh = 227287
        ianonskintbnla = 227918
        fgrasschainnormal = 228041
        fprimitivecalcposvolumeblenddepthvolumedefault = 228164
        fintegratedoutlinecolor = 229134
        bsshadowrecvmultisolidgroup1 = 229368
        ps_imageplanefiltercube = 230207
        fprimitivecalcfresnel = 230557
        fmaterialstdalbedoextendblendvertexalpha = 231237
        ffogvtf = 231522
        ia_skin_tb_2wt = 231881
        vs_materialnull = 232240
        cbcolorcorrectgamma = 232248
        ia_nonskin_bl = 233051
        rsm_param = 233787
        fprimitivecloudcolor = 234347
        shadowcast_output = 235394
        ia_skin_tbnla_8wt = 235566
        ffiltergodraysp2o = 236176
        fmaterialvelocitywposnml = 236641
        fvdgetmaskfromao = 237090
        twaterdepthmap = 237568
        fguicalccolor = 237578
        ia_primitive_sprite = 237862
        iatetradeform2 = 237909
        flocalwindreference = 238842
        fgrasscompressedinput = 239366
        fquaternionaxis = 240222
        ds_materialdm = 240249
        fsamplecount6 = 240413
        calcscatter = 240666
        fcanormalmap = 240891
        finfparticlesamplealbedo = 240946
        tdisplacementmap = 242832
        cbmultishadow = 242967
        fprimitivetessellate = 243567
        fsystemcachecopyy = 244036
        fprocedural1d2e3 = 244350
        prim_fog_out = 244607
        mrtoutput3t = 244958
        tcomparisontexture = 245345
        fwaterrefractionscene = 245529
        getadaptivefactor = 245599
        fshadowreceivefaceattn2 = 245774
        cbgrassunit = 245779
        fprocedural2d2e3 = 245934
        fbokehdefaultfarz = 245950
        fskyfog = 246064
        fshadowlightface3 = 246262
        ttablemap = 247168
        tshadowmapcombine1 = 247731
        fbuildersample = 248091
        bsaddmrt = 248468
        fblurmaskcopycolor = 249636
        fdepthtovariance = 250562
        ia_ambient_shadow = 250595
        tproceduraltexture = 250654
        bsblendrevsubalphargb = 250743
        tdualparaboloid = 250747
        ia_nonskin_tbnl = 251090
        cbcloudmetadata = 251955
        fprimitivecalctexcoordtexel = 252059
        cubemap_filter_output = 252123
        fdynamiceditmapreject = 252465
        fchromaticaberrationfilter = 252724
        ssfilter = 252945
        bsblendaddcolorrgb = 253082
        ldidxtotexcoord = 253760
        fdynamiclight4 = 254210
        bsaddalphargb = 254341
        bsblendinvalpha = 254491
        bsblendnoblend = 254610
        fmaterialstdalbedoprocblendvertexalpha = 255384
        treflectiveshadowmap1 = 255867
        bsmultiplycoloralpha = 256018
        ia_nonskin_tbnca = 257509
        fchannelemissionmap = 257524
        tmaterialconstantlite = 257777
        vs_adhesion = 258557
        ps_deferredlighting_bilateralblurh_size8 = 258954
        fbumphairnormal = 259097
        fprimitivescenesamplerrefractzblurnotex = 259703
        fvertexdisplacementwave = 259941
        focclusionambientmap = 260402
        fradialfiltermaskdisable = 260636
        foutputencodevariance = 261769
        twaterrefraction = 262122
        fmaterialstdfresnelenable = 262298
        iawater = 263457
        ffiltercolorfogcomposite = 263700
        fdefaulttransparency = 263995
        fdeferredlightinggetlightparamfadeout = 264185
        bsmaxalphargb = 264547
        ia_skin_tb_8wt = 265247
        ffiltermotionblursource = 265497
        grass_output = 265703
        fskymapoutputselectmie = 265826
        fgrassbillboardnormal = 266380
        getprojectiontexture = 266521
        prim_eye_out = 267012
        sswrappoint = 267138
        setuplightdiffuse = 267463
        getdeveloptexture = 267547
        ps_sky = 268121
        ps_bloomextractionctr = 268223
        ssfresnelmap = 268657
        fsystemconvertreversehightmaptoparallaxmap = 269072
        cbadhesion = 269262
        fuvemissionmap = 269265
        ia_skin_tbnla_2wt = 269816
        material_input = 269933
        foutlineblendmodulate = 270160
        ssshadowdepthcomp = 270978
        freconstructworldpositiondualpalaboloid = 271490
        fdoffilterlight = 272217
        cbgodraysfilter = 272231
        ps_cubemapvariancefilter = 272399
        fprimitivetransparency = 273410
        fsamplecount = 273547
        ds_materialpn = 273558
        cbworld = 273752
        fdeferredlightingsamplinglightdiscontinuityfiltering = 274352
        bsalphatocoverage = 274671
        fwaterheight2normal = 275026
        ianonskintbn_4m = 275034
        ps_grassshadowreceivezpass = 275192
        cbsoftbodyworldoffset = 275463
        fmaterialstdalbedoextendblendconstantalpha = 276427
        vs_grassdummy = 276639
        cbprimitivecoord = 276821
        fgpuparticlelevelcorrectionneg = 276887
        getaerosoldepth = 277164
        iafilter1 = 277933
        finfparticlevsalphaclipdefault = 278295
        ps_materialdummy = 278668
        fcolormasktransparencymap = 280304
        fwaterbubblenormal = 280497
        falphatestequal = 280920
        ssshadowvariance = 281127
        bsblendcolor = 281132
        material_velocity_output = 281169
        fprimitivecalcfresneldefault = 282084
        fambientshadowdecay = 282290
        bsshadowrecvmultisolidgroup0 = 282478
        ffiltergodraysalphaocclusion = 282901
        fshadowreceivesmoothcascadessmrt = 283550
        fshadowreceivesmoothcascadelsmrt = 283597
        bsrgwrite = 283897
        vs_skymap = 284812
        dsstencilwrite = 285419
        fprimitive2dcalcpos = 285712
        flinearcolorsrgb = 286311
        tnoise = 286651
        fvertexdisplacementcurvev = 287372
        dsoutlineztestwritestenciltest = 287421
        bsmrtwrite1011 = 287552
        ffilterhaze = 287811
        ffilteredgeantialiasinggetedgeweightfast = 288467
        fguigetvertexcolorstatic = 288900
        vs_materialvelocity = 289506
        fprimitivecalcvolumeblenddefault = 289634
        bsawrite = 290211
        cbsystemgamma = 290772
        ffiltervelocity = 290927
        dsguistencilapply = 291837
        vs_dynamicedit = 292591
        tspotlighttexture7 = 292679
        fadhesionalbedosubtract = 292761
        foutlinesample12 = 293135
        ssshadowvariancemip0 = 293458
        tsssdiffusemap0 = 293476
        tantialiasing = 293874
        tfresnelmap = 293978
        fprimitivecalcfogps = 294454
        fprimitivescenesamplerblur = 295573
        tmiragenoisemap = 295836
        finstancing = 296683
        fbumpdetailnormalu_vmap = 297462
        tmaterialdummypicker = 297552
        fswingadjustnormaltangentdisable = 297688
        fprocedural1d2e2 = 297704
        frsmgatherindirectlightingvariable = 298052
        fgpuparticlelevelcorrection = 298075
        rsdefault = 299193
        tvtxdisplacement = 299850
        fcalcprimarycolortoonuber = 299913
        bsblendalphaex = 300446
        fditheringbayer8bit = 300560
        fmiedepthmap = 301575
        treflectwatermap = 301875
        ianonskintbc = 301903
        fsamplecount7 = 301963
        falphatocoverage = 302268
        vs_materialdebug = 302320
        fheightfog = 303324
        finfinitelightd = 303355
        fjointmatrix = 303362
        cbsacan = 303807
        tdynamiceditmap = 304372
        ps_systemps3aadepthcopy = 305067
        fwatertransformvtf = 305243
        fprimitivelevelcorrectionalphalinear = 305665
        foutlinecompositemultiadd = 305691
        fambientshadowcircular = 305836
        fskinningpf = 306391
        fshadowfilterpointpcf4x4 = 306583
        falphatocoveragerop = 306987
        tmaterialnull = 307056
        fmaterialvlocityinflateenable = 307183
        fdepthtest = 307684
        fmaterialstdspecularcolortypeextend = 307917
        fshadowreceivecascadessm = 307924
        fprimitivecalcntbpolygon = 309075
        fguicalcpositiondev2d = 309965
        iagrasspoint = 310165
        flightingdeferredlightingseparatespecular = 310173
        focclusionmap = 310341
        getcubetexturecordinate = 310699
        cbdissolve = 310860
        ia_triangle_index_f32 = 310977
        getopticaldepth = 311936
        fshadowfiltervsm = 312730
        cboutlinemask = 312732
        fsssirradiance = 313107
        fshadowreceivefaceattncut = 313900
        ia_nonskin_tbla = 314093
        fdistancefogtable = 314841
        ps_avgloginit = 314872
        fshadowbias = 315570
        iasoftbodyvertexnovtf = 315782
        fdynamiclight5 = 315796
        fshadowisoutofrange = 316029
        bsdefault = 316104
        samplevariance = 316260
        calclightmask = 316868
        fbruteforcelightingnulllighttexture = 317210
        treflectiveshadowmap0 = 317421
        fprimitive2dlensflareintensity = 318015
        fdeferredlightingencodeparametermrthalflambert = 318964
        cbchannelblend = 319532
        fgpuparticlecalctexcoord = 320225
        fbokehreductionblend = 321319
        cbjointmatrix = 321525
        fblendfogmodulate = 322187
        updatedepth = 322326
        tmaterialstdlite = 322953
        fdynamiceditmapcoordinate = 323289
        fluminance = 323309
        fprocedural2d2e2 = 323640
        fshadowreceivefaceattn3 = 323736
        finstancingmultiplyenable = 323912
        fshadowlightface2 = 323936
        ia_softbody_vertex_novtf = 324776
        ps_fxaa3hq = 325318
        fimageblenddifference = 325350
        tshadowmapcombine0 = 325413
        finstancingstreamsourcematrix = 325600
        cbswingbillboard = 326017
        sbtriangleconstraint = 327382
        decoderippleheight = 327517
        iacubemapfilter = 328215
        fcapsulelight = 328217
        fldtexturesampler3wprev = 328575
        fprocedural1d1e3 = 328743
        fguicalccolorscaling = 329614
        iaambientshadow = 329700
        mirage_filter_ps_input = 329786
        ffogvtfdistance = 330074
        dsztestwritegt = 330248
        fmaterialstdspecularmaskexmodulateproc = 330432
        fradialblurwidth = 330522
        fprimitive2dcalctexcoordnormalize = 331256
        fspecular = 331450
        fdeferredlightinglightvolumelightmasksolid1 = 331773
        fshadowfilter = 331862
        fssaointensitydisable = 332479
        fspotlights = 332731
        ps_gui_dev = 332944
        tlightaccumulationtexture1 = 333088
        fskinningnone = 333090
        fambientmaskenable = 333107
        fprimitiveparallaxscaledefault = 333484
        ttextureblendsource1 = 333546
        fgrassglobalwind_disable = 333657
        bssubawrite = 333682
        fswingoriginfromworld = 333797
        cbvertexdisplacement2 = 333844
        foutlineblendadd = 334327
        fappclip = 334970
        ffresnelschlickrgb = 336182
        bsnowrite = 337176
        fimageblendscreen = 337365
        vs_materialdummy = 338280
        finfparticlecolorconstant = 338931
        ia_skin_tbc_4wt = 339863
        ps_vertexoutput3t = 340061
        swing_info = 340142
        fdiffusesh = 340574
        fspotlightb = 340809
        fambientshadowtexture = 340894
        rsmeshbias12 = 341034
        ffiltercolorcorrectvolumeinterpolateblend = 341141
        ia_skin_tb_1wt = 341904
        sbnormalpackf16 = 342234
        calcpcf4x4 = 342297
        fshadowreceivecascadessmrtlite = 342412
        ftrianglevertex2 = 343601
        tdummy = 343707
        cbsoftbodylwmatrix = 343858
        ianonskintbnl_la = 344111
        vs_vertexoutput = 344744
        tmaterialvelocityedge = 344979
        tambientshadow = 345047
        bsambientmaskgroup2 = 345203
        tcubemapfilter = 345636
        fprimitivecoltexinfluencetexrgbcola = 345660
        vs_modelnormalize = 346766
        bsrevsubcolorrgb = 346818
        fwaterbubbleworldcoordinate = 347022
        ffilteroutlinethick2v = 347055
        material_output_lite = 347639
        fchannelfresnelmap = 347772
        tgsdoffilter = 348229
        fprimitivemodelscenesamplerblur = 348232
        fradialfilteralphacolor = 348822
        freflectspheremap = 348855
        bloom_filter_output = 349123
        getclouddepth = 349606
        fprimitiveparallax = 350041
        morph_input = 350886
        iaprimitivepolyline = 351458
        doadhesiondynamiclighting = 351482
        ps_primitive = 351914
        setuplightspecular = 351919
        dsprimstenciltestneq = 352183
        finfinitelight = 352882
        dsprimzteststenciltestneq = 354031
        fdeveloptexedgefont = 354126
        fsamplecount12 = 354357
        tmaterialconstant = 354416
        fprimitivescenesampler = 354511
        fbokehinversemaskvalue = 354825
        fshadowmultiplereceivert = 354905
        fpointlightdr = 354916
        fshadowreceivert2 = 354964
        ps_cubicblend = 356126
        fprimitivescenesamplerblurnotex = 356311
        rsmeshbias2 = 357297
        fvdmaskuvtransformoffset = 357487
        fuvdetailnormalmap2 = 358111
        ffiltercopy = 359053
        cbjointmatrixex = 359209
        fdynamiclightingdeferredlighting = 359402
        talbedoblend2map = 359452
        tdepthtestmap = 359941
        fprocedural2d1e3 = 360183
        fuvviewnormal = 360587
        material_hs_input = 360661
        sbprimcollision = 361219
        dsprimztestwritestenciltestneq = 361234
        ssenvmaplodbias4 = 361245
        fgpuparticlecalcposparticle = 361617
        dsprimstenciltesteq = 362912
        ffiltermotionblurtilemax = 363627
        ssborderlinear = 364198
        tinfparticle = 364986
        cbdualparaboloid = 365180
        flocalwindloopslot2 = 365794
        flocalwind = 366205
        finfparticlesample = 366372
        sbplaneconstraint = 366718
        cbinfparticletexture = 366873
        ps_bloomfinalout = 367404
        freflectcubemapshadowlight = 367507
        ffilteroutlinesamplecomposite = 368288
        bsguiaddinvcolor = 368533
        fshadowreceivecascadevssmrt = 368669
        fshadowreceivecascadevlsmrt = 368718
        bsguicolorblendalphaadd = 368752
        cbguicoord = 368911
        fprimitivecalcposcloud = 369115
        vs_shadowreceivedeferredrectangle = 370266
        tpointlighttexture6 = 371311
        dsdeferredlightingzteststencilwritedepthpass = 371859
        ia_cubemap_filter = 372177
        fgrassglobalwind = 372683
        fshadowfilter2 = 372817
        cbmorph = 373517
        fbrdffur = 373737
        sbpsskinningaddposps = 374148
        fswing1weight = 375707
        ia_primitive_polygon = 375751
        fdeferredlightinglightvolumelightmask = 375994
        fdynamiclocalwind4 = 376319
        ffinalcombinerscan = 376416
        tguibasemap = 376460
        ia_grass_hicomp2 = 376738
        fprimitiveuvclampdefault = 377000
        ftattooheighttonormal = 377032
        fssaofiltermakelineardepth = 377392
        deferred_lighting_result = 377679
        fgaussianfilterv = 377873
        fradialfiltermask = 377902
        fdeferredlightingsamplinglight = 380048
        fdynamiclightdl5 = 380357
        fwaterdetailcoodinate = 380918
        fshadowreceivecascadevssm = 381119
        ps_materialstd = 382027
        system_mrt4 = 382358
        iaskinbridge4wt4m = 382381
        fmaterialstdalphaalbedovertex = 382731
        fmaterialstdspecularmaskproc = 382893
        fcalcprimarycolorstdlitehemi = 383456
        ftransparencyvolume = 383559
        foutputencodesrgbrrrgb = 383711
        ffilterlightscatteringmulrc = 383816
        fshadowfilterpoint0 = 384117
        fuvtransformoffset = 384155
        tlutfresnel = 384705
        fguicalccoloralphamaskapply = 384752
        fgpuparticleintensitydefault = 385529
        getmiescatter = 385716
        ps_watermask = 385930
        fprimitiveparallaxdefault = 386117
        fprimitivescenesamplerrefractz = 386246
        fvertexdisplacement = 386757
        ps_shadowreceivetransparent = 386917
        ianonskintbn = 387058
        ia_skin_tbn_4wt = 387878
        fvariancefilterh = 388275
        fprimitivemaskmap = 388718
        fldlatticedeformer = 389008
        fdevelopdecode_rgbi = 389300
        fdamagesimplealbedomapburnmap = 389792
        ffilteroutlineblur2h = 390111
        tgpuparticle = 390176
        ps_materialdebug = 390420
        fvduvextend = 390445
        fprimitivelevelcorrectionalphapos = 390819
        ia_instancing_color = 391922
        fblendshininessmap = 392906
        fsamplecount26 = 393199
        ssshadowvariance2 = 393377
        bsrevsubblendcolor = 393620
        fradialfiltersamplecolorscale = 393888
        hs_pn_constant = 394064
        tvolumemap = 394215
        fmaterialstdalbedoextendadd = 394377
        tsoftbodytexbox = 394581
        fvertexdisplacementwaveplus = 395119
        ssdistortionmap = 395126
        foutlinedetector3 = 395293
        bsaddbwrite = 396196
        sb_input = 396731
        tpointlighttexture0 = 397146
        correctdepthsub = 397168
        fbumpdetailnormalmap = 397477
        fworldcoordinatelatticedeformedge = 397520
        astral_body_vs_out = 398187
        cbcolorcorrectcolor = 398240
        ftransparencymapalphaclip = 398746
        fmaterialstdalbedoextendmodulate = 398929
        tfogfrontdepth = 398958
        ffresnelschlickmap = 399327
        fprimitivesamplealphamappoint = 399503
        fdynamiclocalwind2 = 399562
        vs_grassoutsourceing = 399703
        bsaddcolorrgb = 400100
        ia_water_ripple = 400186
        cbvertexdispmaskuv = 400494
        bsrwrite = 400790
        cbvertexdisplacementexplosion = 400963
        fshadowreceivelsm = 401028
        gpu_particle_vs_input = 401850
        fdiffusethinsh = 402375
        fuvshininessmap = 402979
        ssenvmaplodbias2 = 402984
        fskycorrecthorizonenable = 403298
        bsblendaddalphargb = 403451
        bsblendrevsubcolorrgb = 403478
        fsssgaussianfilterh = 403948
        bssolid = 404269
        variance_filter_output = 404305
        sbfilterdepthnormps = 405128
        fdissolve = 405307
        tdistortionblend2map = 405470
        ssemissionmap = 405534
        falbedotextureblendmapviewnormal = 405924
        tmiedepthmap = 406172
        tprocedural1d2 = 406653
        vs_primitivetessellate = 406827
        ianonskintbnl = 408428
        ps_adhesion = 408510
        ps_dynamicedit = 408921
        fambientsh = 409258
        fuseglobaltransparency = 409260
        fwaterreflectionenvironmentmap = 409610
        tsoftbodysrctex6 = 409932
        fprimitivecloudenv = 410654
        iaprimitivecloudbillboard = 410677
        iaskintbnla4wt = 411027
        adhesion_output_pv = 411282
        fprimitivecalctexcoordnormalize = 411722
        tcolormodifieropticalcamouflagemap = 412566
        tenvmap = 412739
        ps_imageplanefilterbaseex = 412742
        fgrasschainposition = 413035
        finfparticletexturepatternanimate = 413176
        fswingdisable = 413466
        bsambientmaskalphagroup0 = 414574
        ps_transitiondynamicedit = 415284
        fwaterunitprotfrommodel = 415865
        fmirageclamp = 415941
        ps_skysunbody = 416383
        fsamplecount20 = 416474
        cbvertexdisplacementranduv = 416679
        bsfogblend = 416786
        shadowcast_input = 417124
        fuvtransformextend = 417639
        ttangentfilter = 419035
        tlightshaft = 419447
        iaskintbn1wt = 419761
        fprojectiontexturecolorr = 419819
        fswingupdate = 420020
        fdynamiclightdl3 = 420080
        fvduvprimary = 420129
        vs_materialconstant = 420243
        calcwavephase = 421302
        grass_shadowreceive_output = 421373
        vdunpacku8u8n = 421413
        tshadowreceive = 421674
        fuvtransparencymap = 421740
        bsmrtwrite0100 = 421829
        system_mrt2 = 422051
        frimaddcolor = 422165
        fprimitivetonemap = 422403
        fchanneldetailmap = 422444
        vs_materialstdest = 422573
        fshdiffuse = 422934
        bssolidex = 424231
        getmaterialshadowrt = 424465
        tsoftbodytexcapsule = 425090
        cbblurmask = 425829
        finfparticleposbezier = 426127
        bsblendblendcolor = 426264
        fprimitiveparallaxscale = 426281
        fshadowfilterpcf4x4 = 426347
        fprimitive2dcalcpossprite = 426630
        fshadowmultireceivelsmrt = 426721
        ia_develop_prim3d = 426781
        fprimitivesamplealphamapparallaxpoint = 427360
        fquaternionrotationarc = 427567
        fbluralphamask = 427585
        ldnormalpackf32 = 428325
        fbokehantibleedinginversemaskvalue = 428402
        ps_dummypicker2 = 429083
        fdeveloptexture = 429269
        fgpuparticlecalcdepthblenddefault = 430310
        fdeferredlightinggetlightparam = 430423
        fshadowreceiveattn2 = 430522
        fdynamiceditmapcoordinateenable = 431032
        fswingbillboard = 431704
        fspotlightd = 431740
        fdeferredlightingencodelineardepth = 432168
        fprocedural2d3e2 = 432655
        fbumpmapfromgbuffer = 432838
        fdebugviewpixelbasemapalpha = 433016
        fvertexdisplacementcurveuv = 433259
        pointlighttexture = 433346
        ps_fxaa = 433374
        fsssfillmarginh = 433847
        cbguimatrix = 434428
        bsrevsub = 435587
        deferred_lighting_light_volume_vs_output = 436246
        vs_fxaa = 436708
        fcalcprimarycolorconstantlitedefault = 436732
        fprimitiveocclusionsphere = 437021
        primitive_dc_output = 437104
        tindirectmap = 437118
        fdegammadesable = 437393
        fjointmatrixfromcbuf = 437730
        flightmaskshadowmultirt0 = 437821
        cbshadowreceive3 = 438184
        fmaterialstdspecularmaskdefault = 438429
        ffogdistanceest = 439165
        fxaa3 = 440223
        primitive_vs_input = 440561
        tvolumeblendmap = 440669
        vs_dummy = 440825
        fskinningpf4weightbranch = 441255
        sbpsskinningps = 441366
        fgrassconstraintbillboard = 441976
        sb_psmrtout2 = 442490
        fradialfilteralpha = 442755
        fbdistortionrefract = 443725
        cbcolorcorrectmatrix = 444205
        cbmaterial = 444417
        ps_filterdepth = 444755
        fsamplecount14 = 445696
        bsblendnoblendrgb = 446136
        bsazero = 446145
        tfrontparaboloidmap = 446464
        projection_input = 447162
        cbviewfrustum = 447830
        iabuilder = 447957
        rsmeshbias4 = 448132
        ps_tangentfilter_blur4 = 448288
        cbburncommon = 448552
        sbisccalcbk = 449158
        falphatestnotequal = 449894
        fworldcoordinateswing = 450015
        cbgrasschain = 450075
        fdevelopdecode_r = 450201
        fprocedural1d3e2 = 450783
        flightmaskrtsolid0 = 451738
        iatrianglef32 = 451997
        fsystemconvertreversehightmaptonormalmap = 453035
        cbdevelopflags = 453289
        ia_nonskin_bla = 453364
        tsoftbodytexsphere = 454025
        trayleighscattermap = 454073
        fpointlightsr = 454386
        cbcolormask = 454678
        tsimwatersimpletex = 455839
        calcpmax = 456218
        ps_normalizedseparation = 456987
        fprimitivecalcposcloudbillboard = 457383
        fgrassuvmixer = 457722
        fwindsincoscurve = 457734
        cbsoftbodyrtparam2 = 459024
        fprimitivemodelsmoothalphavertexnormal = 459344
        fwaterwposprotfrommodel = 460228
        finfinitelightb = 460238
        procedural_texture_out = 460472
        fbokehnearcopy = 460671
        fbokehreductionfarz = 461420
        ia_filter1 = 461648
        ffiltergodraysscaleocclusion = 462474
        frimmodulate = 462694
        sswraplinear = 462851
        simwater_for_view_ps_input = 462930
        iainfparticle = 463096
        fprimitivelevelcorrectionpos = 465380
        flightingvs = 465836
        fswingviewi = 466958
        fgrasscossin = 466975
        fprimitiveocclusionfactor = 467354
        fprimitivecalccolorint = 468056
        ffilteroutlinethick1h = 468239
        finfinitelights = 468284
        falbedomapblenduv = 468389
        tfogbackdepth = 468669
        cbappclipplane = 468830
        tprimalphamap = 468888
        fgrassadjustnormaldisable = 469045
        fpervertexlightingtoonvs = 469350
        ffiltercolorcorrectvolumeblend = 470453
        fprimitivecoltexinfluencedefault = 470548
        ffogdistancetableest = 470577
        frsmcomputeindirectlighting = 470679
        ffiltermotionblurreconstruct = 470811
        ia_gpu_line_particle = 471206
        fimageblendlighten = 471235
        iaswing2 = 471896
        fgrassbillboarduv = 472136
        fprimitivesamplealphamaplin = 472348
        cbsystemmiptarget = 473628
        fprimitivesamplealphamapparallaxlin = 473717
        tshininessblendmap = 474004
        fdiffuselightmapocclusion = 474383
        fdebugviewpixelocclusion = 474487
        fshadowfilterpcf3x3comp = 474510
        fswingadjustnormaltangent = 474730
        fsamplecount1 = 474814
        sbinitps = 474856
        fskinning1weight = 475321
        fldtetradeformer = 475851
        tfogtablevtf = 476305
        shadowreceiveparam = 476452
        fprimitivescenesamplerrefractznotex = 476882
        fddmaterialcalcborderblendalphamap = 477117
        ianonskintbna = 477137
        sampleweight = 477211
        colorlerp = 477328
        fcollisionsimplevs = 478953
        fdamagespecularmap = 479956
        fvariancemakemiplevel = 480173
        cbdeferredlightingdiscontinuitysensitivefiltering = 480591
        fbrdfhair = 481402
        ps_radialblurfilter = 481463
        tprimdepthmap = 481574
        vs_skystar = 481636
        tdetailnormalmap = 481875
        ps_systemdepthhmax = 482209
        iaskintbn8wt = 482366
        tnormalblend2map = 482623
        fprocedural1e = 482770
        ia_nonskin_tbn_4m = 483216
        spotpointlighttexture = 483726
        fsystemconverthightmaptonormalmap = 483945
        cbbilateralfilter = 484038
        fblendalbedomap = 484166
        fprimitivescenesamplerrefractnotex = 484483
        fshadowlightface = 484806
        tcloudscattermap = 484994
        bssubrwrite = 485191
        iainstancing = 485770
        tmaterialvelocity = 486145
        tangent_filter_out = 486247
        falbedomapblendcoloronly = 486645
        ps_primitivetessellate = 487339
        cbpicker = 487389
        fmaterialstdfresneldefault = 487488
        fprimitivecalcvolumeblendps = 487518
        fdebugviewpixel = 487539
        fspeculardisable = 488441
        fdynamiclight3 = 488609
        fguicalcuvalphamask = 488610
        iagpuparticle = 488802
        fgrassnormal = 489242
        ftvnoisefilterscanline = 489722
        ffiltermotionblur4 = 490783
        iaskintbc4wt = 490887
        fgrasschaintangent = 491010
        fddmaterialspecular = 491011
        ttextureblend = 491784
        fuvtransformprimary = 492037
        ssthinmap = 492049
        iavertexindexf32 = 492320
        ia_sky = 492674
        ia_gpu_polyline_particle = 492689
        dsguizteststencilapplyreverse = 493259
        ds_materialph = 493987
        ffilterlightscattering = 494253
        dsambientshadow = 494889
        ps_systemdownsample4emphansis = 495859
        getoccludermatrix = 495930
        sbidxtotexuv = 496219
        tbuilder = 496641
        dsguiztestwritestencilupdate = 496783
        flightmaskenable = 497145
        fprimitivesample = 497309
        primitive_hs_const_data = 497332
        bsgodrays = 497415
        ps_variancefilter = 497470
        fprocedural1d4e0 = 497526
        tmiragedepthmap = 497540
        cbmaterialtoon = 497834
        tsoftbodytexdepthnorm6 = 497957
        cbbloomgaussblur = 498102
        iasoftbodyvertex = 498270
        convzvalue = 498347
        primitive_hs_input = 498664
        ffilteroutlineblur1v = 499071
        foutputencoderrrgb = 499146
        vs_materialstd = 499709
        fcalcprimarycolortoondefault = 499812
        fbrdfhalflambert = 500529
        fbruteforceapproximatelighting = 501173
        fvariancefiltercubedirv = 501201
        fmarklooppoint = 501644
        fprimitivecalcpospolyline = 501774
        fshadowisoutofrange3 = 501829
        ia_vertex_index_f32 = 501847
        tmaskmap = 501998
        rsmeshbias9 = 502329
        cbsystemdepthcopy = 502426
        iadevelopprim2d = 502778
        cbdebugview = 502779
        fclampsceneuv = 502801
        bsblendblendcolorrgb = 502938
        fgrasslightmask = 502949
        talbedoburnmap = 503623
        fsamplecount19 = 504253
        globals = 504514
        tsoftbodytexellipsoid = 504580
        theightmap = 505201
        fog_out = 505303
        tfogfrontdepthsmall = 505671
        vs_ssaomakenormal = 505756
        fbokehbleeding = 505838
        focclusion = 506348
        tprocedural2d3 = 506546
        fambientshadowcircularspread = 506947
        fprimitivecalcfogblend = 507398
        mirage_heat_ps_input = 507722
        fprimitivemodelsmoothalpha = 508021
        gs_dof_output = 508947
        tmatrixpfmap = 509808
        fmaterialstdalphaalbedo = 509819
        cbfog = 509996
        getdepthcolumn6 = 510023
        bsaccumulatecoloralpha = 510446
        ffilteredgeantialiasingdynamicbranch = 510465
        ps_materialsssirradiance = 510660
        fssaoapplyambientocclusion = 510781
        fpervertexlightingps = 510905
        maskoutlinechannel = 511648
        iagsdoffilter = 512263
        vs_develop3d = 512576
        tspotlighttexture1 = 512626
        dsztest = 512758
        ssspecularmapclamp = 512770
        ffilterhermitetonecurve = 513037
        bsaddalphaex = 513083
        frimblend = 514532
        bsshadowrecvsolidgroup1 = 514628
        tsoftbodytextriangle = 515137
        fbluralphamaskenable = 515216
        fchromaticaberrationfilterhq = 515271
        fintensityweightrgba = 515335
        fchannelr = 515595
        fuvfresnelmap = 515656
        bsshadowrecvtransparentgroup0 = 517392
        fdeferredlightingsamplinglightdiscontinuityfilteringlayer1 = 517552
        fditheringbayer10bit = 518002
        fgpuparticlesamplenotexture = 518297
        tblendratemap = 518570
        vs_skyastralbody = 518912
        ialatticedeform = 519128
        fprocedural2d4e0 = 519590
        fmaterialstdvertexcolorshadowdefault = 520322
        fcolormodifieropticalcamouflage = 521162
        fwatertransform = 521189
        ps_bloomdownsample4 = 521627
        ps_deferredlighting_bilateralupsampling = 522805
        iasystemclear = 522869
        fgrasschainuv = 523062
        ia_inf_particle = 523973
        ps_bloomgather = 524408
        ssnormalmapclamp = 524424
        calclightshaftsearchlength = 524909
        bsmrtwrite0011 = 525349
        ssspecularmap = 525374
        bsrevsubblendcolorrgb = 525403
        fheightfogworldy = 525606
        bsblendaddalpha = 525680
        fdynamiclightdl1 = 526812
        ffilterscreentexcoord = 527068
        ftexbeckmannmodel = 527236
        fshadowreceiveattnspotfade = 527941
        fdeferredlightingdecodeinputexponent = 528054
        tvirtualcubeshadowfaceselection = 528803
        sbsolveconstiscps = 528867
        iaprimitivepolygon = 529594
        ftattoouv = 529649
        bsblendrevsubblendalpha = 529675
        ftexanisotropicphongdiffusegmodel = 529906
        fwatershadowreceivesinglelsm = 529946
        ffilteroutlinethick1v = 530540
        fshadowreceiveattn = 530554
        fsimwatersimpletexps = 530869
        bsmul = 531924
        iasoftbodydecouplenovtf = 532431
        tsoftbodysrctex4 = 532576
        fdistanceattenuationsquarelaw = 532742
        fuvtransformoffsetlite = 534009
        fchannelocclusionmap = 534068
        fprojectiontexturecolora = 534069
        fdebugviewvertexprelight = 534546
        fskinning = 534549
        shadowreceivecontext = 536080
        cbprojectiontexture = 536799
        bsambientmaskalphagroup2 = 537154
        iagpulineparticle = 537506
        fprimitivesamplebasemapparalaxlin = 537583
        ffilterhazeinverse = 537855
        ffilteroutlinecompositebloomf = 538735
        fskymapbeginend = 539461
        fsamplecount22 = 539638
        cbhdremphasis = 539921
        cbratemap = 540949
        fperpixellightingtoonps = 541020
        fguicalcposition2d = 541149
        fprimitivelevelcorrectionalphaneg = 541742
        vs_watermask = 542314
        fprimitivecalcnormalmapparallax = 542710
        fprimitivecalcshadecolor = 543335
        foutlineblendhdrencode = 543373
        falphatest = 544529
        cbsbviewprojection = 544530
        tradialblurfilter = 545351
        ia_skin_tbc_2wt = 545573
        fsystemconvertbasemaptonormalmap = 546122
        tprocedural1d0 = 546129
        fbokehcompressrangefactor = 546353
        fshadowfilterpcf2x2 = 547052
        vs_infparticle2 = 547523
        cbnvmodel = 547643
        ps_avglogfinal = 547945
        tmiragescenemap = 548442
        ps_materialsssdistortion = 548819
        cbprimitivetessellationcmn = 549251
        ssshadowvariance0 = 549261
        fskymapoutputselectrayleigh = 549352
        ps_materialvelocity = 549361
        bsasub = 549462
        bsmrtwrite1000 = 549527
        fmaterialstdreflectiontypedefault2 = 550161
        foutlinedetector1 = 551217
        fimageblenddarken = 551324
        fuvdistortionmap = 551493
        fdynamiceditmapscaling = 552484
        tpointlighttexture2 = 552566
        tssaobackfacedepthmap = 552715
        mirror_filter = 552786
        fworldmatrix = 552913
        femission = 552983
        ia_skin_bridge_4wt_4m = 553338
        fperpixellightingvs = 553581
        filter_input = 553713
        hs_ph_constant = 553751
        cbshadowreceive = 553940
        dsprimzteststenciltesteq = 554214
        water_position_output = 554237
        flightmasksolid1 = 554262
        fwatercaustics = 554387
        iainstancingcolor = 554778
        cbtangentfilter = 555045
        vs_miragesect = 555397
        fdynamiclocalwind0 = 555494
        tdeferredlighting = 555594
        bsaddrgb = 556444
        cbprimitivemetadatauvclamp = 557139
        tdetailmaskmap = 557413
        fprocedural1d3e0 = 557555
        fskinningpf1weight = 557611
        foutputencodesrgbrrrgbi = 557995
        fprimitiveuvoffset = 558980
        fgpuparticlesamplebasemaplin = 559436
        updateclouddepth = 559525
        sbtexcoordtopositionx = 559610
        fambientshadowdecayperspective = 559946
        fmiragecalcoutput = 560028
        fviewproj = 560175
        tsoftbodytexterrain = 560816
        tprimscenemap = 561400
        calcwaveplane = 562941
        ia_skin_tbn_2wt = 563092
        fbokehantibleedingmaskvalue = 563303
        fvariancefiltercubedirh = 563378
        fcalchemispherelight = 563575
        fmaterialstdalbedoprocalphablend = 563984
        fdistortion = 564642
        fdevelopdecode_a = 565063
        ffilteroutlineblur1h = 565276
        tmaterialdummyedge = 565315
        ttextureblendsourcecube0 = 565764
        finfparticletexturepatternindependent = 565932
        fprimitivecalcfogpsdefault = 565947
        primitive_hs_control_point = 566069
        fbrdf_lite = 566224
        develop_output = 566768
        ianonskinbl_la = 566808
        bsblendcolorex = 567562
        fheightfogvolume = 567582
        fsamplecount16 = 568364
        vs_materialconstantlite = 568683
        cbgpuparticletex = 570494
        mirage_heat_vs_input = 571085
        cbblurmaskintermediate = 571204
        rsmeshbias6 = 571304
        sb_output = 571543
        fbokehnearfilter = 571976
        fshadowreceivesmoothcascadelsm = 572054
        fswingupdateall = 572690
        fprimitivecalcdiffusenormalmap = 573686
        dsnvstenciltest = 573794
        dsguizteststencilapply = 574119
        ssdetailnormalmap = 574654
        tcubeblendmap = 574881
        ffresnelschlick = 575195
        calcparticleratio = 575828
        cbshadowreceive1 = 577156
        ia_primitive_nt = 577875
        ia_skin_bridge_1wt = 579791
        fdebugviewpixeltangent = 581483
        ftransparencyalpha = 582986
        cbprimitivemetadataocclusion = 583157
        vs_primitive2d = 583275
        finfparticlerandomizeposdefault = 584184
        triangle_output = 584682
        ps_dummypicker0 = 585015
        fdecodersmparameter = 585600
        freflectcubemap = 585729
        fshadowreceiveattn0 = 585878
        treductionblendmap = 586303
        finfparticlecolorlerp = 586949
        sbnormalunpackf16 = 586993
        lattice_deform_input = 587894
        cbprimitivemetadatalvcorrection = 587996
        fprocedural2d3e0 = 588579
        vs_primitive = 588618
        ps_systemclearmrt2 = 588902
        fspecularmapblendtransparencymap = 589121
        fdevelopdecode_font = 589979
        fwaterrefractionocean = 590045
        sbapplyworldoffsetps_xbox = 590729
        ttattoo = 591327
        ftransparencymap = 592138
        sslinearmippoint = 592282
        tindirectmaskmap = 592577
        tmaterialoutline = 592625
        vs_system = 592840
        fswingbillboarddisable = 592962
        cbimageplane = 593689
        fprimitivesamplenotexture = 593767
        ia_softbody_decouple = 594104
        fuvprimary = 594546
        hs_materialdm = 594818
        vs_mirage = 594927
        fsssgaussianfilterv = 595087
        fdynamiclight1 = 595341
        tsimwaterforview = 595814
        calcscreenztoviewdepth = 596577
        fmaterialstdspecularcolortypedefault2 = 596627
        fbokehantibleeding = 596979
        finfparticleposspline = 597260
        getopticaldepthmap = 597581
        tprimnormalmap = 598282
        fvdmaskuvtransform = 598528
        fclampsceneuvsmooth = 598533
        rsmeshcn = 598835
        ssalbedomapclamp = 598920
        fwaterbubble = 599055
        ps_avglog16 = 599496
        ianonskintbnc = 599805
        gpu_particle_ps_input = 600125
        ps_skystar = 600355
        ffeedbackblurfilter = 602453
        tfiltertempmap1 = 602551
        getclouddepth2 = 602632
        sbpassthroughvs = 602960
        ffiltergodrayscopy = 603880
        hsv2rgb = 604419
        ianonskintbca = 604572
        ps_ssaomakesinglefaceocclusionmap = 604609
        ssp2o = 605045
        sslinear = 605119
        ia_texture_blend = 606431
        ffiltergodraysscale = 606658
        tvariancefilter = 607109
        cbscreen = 607341
        bsblendalphargb = 607651
        bsaddinvalpha = 607805
        dsguizwritestencilupdate = 608261
        dsprimztestwritestenciltesteq = 608432
        ps_textureblendcube = 609014
        lightshaft_output = 609048
        fshadowreceiveattnfade = 609112
        ps_waterripple = 609530
        fmaterialstdreflectiontyperim2mask = 609947
        fgpuparticlefogvscolor = 610244
        cbprimitivedebug = 610575
        ftexorennayar = 610650
        fbrdfskin = 610685
        fsystemcopy = 610692
        cbsky = 610768
        ps_shadowcastzoffset = 610896
        fdeferredlightingencodenormal = 611554
        fmaterialstdreflectiontypevertexcolorrim = 611640
        ia_lattice_deform = 612435
        fprimitivescenesamplerdistortionnotex = 612554
        ftexanisotropicphongspecularmodel = 613348
        fsamplecount3 = 614290
        ps_materialnull = 614338
        tattoo_output = 614627
        ia_skin_tbnla_4wt = 614730
        ffogvtfdistancetable = 614773
        fssaobouncedisable = 614840
        cbguialphamask = 614850
        iatattooblend2d = 615044
        cbwaterbubble = 615160
        fdebugviewpixelbasemap = 615497
        cbprimitivemodel = 615537
        fimageblendhardlight = 616039
        ffiltergodraysiteratorsc = 616138
        ps_ssaomakeocclusionmap = 617359
        fprimitivecalccolorintdefault = 617841
        ia_bokeh = 618046
        vs_shadowcast = 618095
        ia_grass_spu_input = 618894
        fwaterwindtransform = 618944
        bsminalphargb = 619116
        dsguizteststencilupdate = 620037
        frsmgatherindirectlightinglargesize = 620604
        ps_mirror = 620675
        ssocclusionmap = 620687
        vs_cubemapvariancefilter = 621151
        instancing_input = 621278
        iafilter = 621589
        fsystemcachecopycr = 621819
        cbmaterialsss = 621873
        fbrdfbeckmann = 622099
        iaastralbody = 623131
        flocalwindline = 623627
        cbinstancematrix = 623708
        bsblendrevsubalpha = 624154
        fgpuparticlelevelcorrectionpos = 625434
        fspotlightdr = 625497
        fprocedural2d4e2 = 625802
        foutputencodergbi = 626238
        ps_deferredlighting_gbufferpassmrtest = 626469
        cblocalwind = 626803
        ps_systemtonemapdepth = 626929
        sbinitps_xbox = 627826
        sbsolveconstps = 627892
        tguiblendmap = 628478
        tblendmap = 628817
        sbsolveconstps_xbox = 628893
        ffiltermotionblurreductionblend = 629583
        fcalcprimarycolorstdlitealphadefault = 629663
        sswrapanisotoropic = 630367
        fswingjointsupport = 630491
        getintensitybothfaces = 630626
        ps_watershadowmap = 630640
        fchannela = 630741
        fsssfillmarginv = 631764
        fwaterbubbledepth = 632002
        fguicalccolorattribute = 632023
        grass_outsourcing_input = 632194
        cbblendfog = 632538
        fgpuparticlefogps = 633065
        twcvtfpos = 633163
        fgrasstangent = 633185
        twindmap = 633446
        fvertexdisplacementdiru = 633604
        falbedomapmodulate = 633617
        ps_dummy = 635006
        vs_dualparaboloid = 635080
        fchannelthinmap = 635101
        fuvspecularblendmap = 635268
        cblatticedeform = 635669
        tspotlighttexture3 = 635742
        fdispersionmap = 636278
        ia_tetra_deform2 = 636331
        fgrassperpixelshading = 636702
        ia_softbody_vertex_ps3 = 637464
        ps_deferredlighting_gbufferpass = 637545
        foutlinefadedepth = 637686
        ps_systemdownsample4hdr = 638122
        foutlinedetectorid = 638500
        tsssdiffusemap4 = 638589
        ia_tattoo_blend2d = 638935
        fuvindirectsource = 639313
        fwatercausticsdisable = 640659
        ffiltercolorcorrectvolume = 640868
        fshadowisoutofrange1 = 641385
        ia_gsdoffilter = 641484
        fradialblurwidthocclusion = 641652
        fguicalccolorattributeon = 641877
        cbpsdiscardmaterialparamcommon = 642033
        ps_grass_deferred = 642048
        ps_imageplanefilterbase = 642278
        ps_developedgefont = 643077
        fmiragerefractdefault = 643546
        vs_grassshadowreceive = 644291
        fheightfogmodelsimplevtf = 645015
        fshininess = 645051
        ffiltercomposite = 645622
        fprimitivecalcintensitydefault = 645778
        tprocedural2d1 = 646046
        calczoffset = 646192
        fmirrorfilter = 647107
        fmorph = 647202
        ia_skin_bridge_8wt = 648000
        fmatrixtoquaternion = 648156
        fprimitevecolormodifier = 649504
        falbedomapmodulateuv = 649849
        ps_systemocclusionconvertz = 650450
        ps_waterwposb = 650699
        fprimitiveocclusionfactoroccmap = 651113
        shadowreceive_deferred_output = 651494
        fclampsceneuvclip = 651558
        fcolormaskalbedomapmodulate = 651946
        fdistortionrefract = 652114
        ia_tetra_deform = 652380
        tmaterialstdpn = 652565
        fprocedural1d4e2 = 652890
        tsoftbodytexdepthnorm4 = 653321
        fadhesionalbedo = 654899
        fprimitivetransparencyvolume = 655121
        iaskintbc2wt = 655669
        mirage_filter_vs_input = 655805
        creatematerialcontextlite = 656256
        twaterbubblemask = 657272
        bsblendfactor = 657328
        sslightmap = 657417
        bsmrtwrite1100 = 657568
        ia_deferredlighting_lightvolume = 657784
        foutlinecompositeblend = 658032
        initmaterialcontextlite = 658409
        fprocedural2e = 658961
        fspecularreflectancemodel = 659125
        fspotlightsr = 659407
        ianonskinbca = 660704
        ia_collision_vs_input = 660888
        bsrevsubinvalpha = 661019
        tspotlighttexture5 = 661099
        tsssdiffusemap2 = 662344
        cbshadowcasterrasterizerstate = 662884
        fgpuparticlecalctexcoordnone = 663000
        tmaterialhud = 664095
        tvertexpositionsubmap = 664189
        fdeferredlightinglightvolumelightmasktransparent1 = 665089
        tfogbackdepthsmall = 665571
        fprimitivealphatocolordefault = 665735
        fdistancefogtablevtf = 666639
        fdeferredlightingencodeparameterhalflambert = 666773
        cbbokehcomposite = 667092
        fuvspecularmap = 667633
        bsrevsubcolor = 668135
        iaskinbridge8wt = 668172
        dsguistencilapplyreverse = 668190
        fdiffusevertexcolorsh = 668275
        fdiffusereflectancemodel = 668407
        fskinning4weightbranch = 669038
        fchannelg = 670432
        flocalwinddirection = 670810
        ps_filter = 670932
        twaterbubble2 = 671057
        fuvtransformoffset3 = 671238
        fwatercausticsfilter = 671461
        tmirage = 671772
        foutlinecompositeadd = 671888
        fprimitivemodelsmoothalphainverse = 672397
        cbgpuparticleex = 672658
        tspecularburnmap = 673342
        ffogvtfnone = 673511
        tmaterialsss = 673957
        ssao_normal_out = 674795
        material_outline_output = 675227
        flocalwinddisable = 675723
        tmaterialstdph = 675872
        bsblendrevsubblendalphargb = 676032
        tbackparaboloidmap = 676583
        tluttoon = 677203
        vs_tattoo = 677420
        ssprocedural = 677724
        tsystem = 677947
        fsamplecount31 = 678669
        ffiltergodraysthreshold3dbound = 679053
        tsoftbodytexdepthnorm2 = 679228
        fuvextend = 679242
        vs_cloudprimitive = 679265
        ps_materialconstant = 680576
        iagrasshicomp = 681041
        fimageblenddodge = 681827
        fchannelblend = 681941
        cbtonemapfilter = 683266
        bsmrtwrite0111 = 683538
        fldtestdeformer = 683728
        ftangentmodifier = 683889
        sbcreatedepthnormbackps = 684008
        ps_textureblend = 684474
        cbprimitivemetadatashade = 684674
        fmaterialstdvertexocclusionenable = 684677
        fshadowfilterpointpcf2x2 = 685072
        ttestmap = 685100
        fcalcshadowmapuv = 685534
        ffilteroutlinethick2h = 685772
        fcubemapvariancefilter = 686215
        cblightshaft = 686716
        decodesrgb = 686753
        ps_tvnoisefilter = 687031
        ianonskinb = 687485
        twatersurfacemap2 = 687891
        fgrassshapeinvisible = 688205
        rsm_output = 688278
        bsblendblendadddestalpha = 688613
        falbedomap = 688746
        filtercascadevssm = 688775
        ssanisotoropic = 688844
        fdiffuseconstantsrgbvertexcolor = 689680
        ssdevelop = 690954
        fcalcprimarycolorconstantliteuber = 691190
        iagrass = 691720
        frimnone = 691937
        iaskintb1wt = 692139
        fanisotropicphongspecularmodel = 692186
        fshadowlightface0 = 692300
        fprocedural2d2e0 = 692500
        cbwatercaustics = 692652
        fshadowreceivefaceattn1 = 692660
        sampledepthcomp = 692785
        fdebugviewvertex = 692878
        fprimitivecalcposvolumeblenddepthvolume = 693149
        fgrassinput = 693511
        tshadowmapcombine2 = 693769
        dszwrite = 693884
        fpervertexshadowfilter6x6 = 693978
        fshadowbiasdisable = 694024
        tshininessmap = 694151
        fshadowreceive = 694251
        sky_star_out = 694772
        tprimmaskmap = 695837
        fwaterdetailnormal = 696391
        ps_systemps3aacopy = 696480
        falphatestalways = 697011
        tlightmap = 698096
        fkelemenszirmaymodel = 698905
        fprimitivelevelcorrectionneg = 699241
        bsshadowrecvmultitransparentgroup1 = 699301
        fgrassuvmixerenable = 699693
        ps_primitive2d = 699869
        fdynamiclight7 = 700600
        material_context_lite = 701377
        ia_skin_otb_4wt_4m = 701589
        fwatershadowreceive = 701808
        fprimitivepsocclusion = 702277
        fmiragecalcoutputnoise = 702304
        ffiltergodrays8samplesiterator = 702557
        fheightfogmodelsimple = 702801
        cbskinning = 702818
        iasimwaterforviewinput = 704150
        iasystemcopy = 704229
        fmiragemodcolor = 704374
        freflect = 705367
        ps_shadowreceivedeferredrectangle = 705648
        fdebugviewpixelprelight = 705851
        ps_tattoonormalblend2d = 705916
        fworldcoordinatefromtexturecalctangnet = 706505
        ffilteroutlineblur2v = 708284
        calccurveposition = 708710
        fvariancefilterv = 709072
        cbchromaticaberration = 710191
        ftransparencydodgemap = 710329
        falbedomapblendtransparencymap = 711042
        fshadowreceivert = 711265
        waterwindeffect = 711297
        fthresholdreactionemissionmapclipping = 711395
        finfparticlecolor = 711802
        cbinstanceid = 712089
        ssinfparticlepoint = 712108
        fmaterialvelocitywposnmlsoftbody = 712125
        foutlinesample4 = 712582
        fdepthtestgt = 713193
        fsamplecount29 = 713342
        cbmotionblur = 713589
        twaterenvironment = 713605
        ssao_output = 713885
        sbpositiontotexcoordy = 714240
        fswingorigindefault = 714405
        material_hs_output = 714565
        fprocedural1d2e0 = 715716
        ssgrass = 716312
        cbbalphaclip = 716343
        ffiltergodraysbegin = 717139
        fprimitivecalcpos = 717208
        fprimitivecalcshadecolorratio = 718159
        fprimitivecalcfogalpha = 718404
        fssaoapplyindirectbounce = 718677
        outline_detector = 718706
        fmaterialstdspecularcolortypealbedo = 719064
        fgaussianfilterh = 719218
        ianonskintba = 719459
        fsamplecount5 = 719527
        fspotlight = 719736
        ffiltercolorfogblend = 720270
        falphatestnever = 720575
        fuvthinmap = 720576
        fshadowcast = 721695
        cblightvolume = 721909
        vs_transitiondynamicedit = 722020
        vs_waterripple = 722764
        tocclusionquery = 722769
        fsamplecount10 = 723225
        fprimitivevsalphaclipdefault = 723250
        fworldcoordinatelatticedeform = 723282
        iaskinbridge1wt = 723331
        fshadowreceivert0 = 723896
        ffinalcombinernofog = 724402
        getshdiffuse = 724587
        fmaterialstdalbedoprocadd = 725365
        vs_tvnoisefilter = 725587
        fmaterialstdreflectiontypeproc2 = 727163
        fmaterialstdspecularmaskexvertexcolorb = 727200
        fdeferredlightinglightvolumelightmaskrtsolid1 = 727220
        cbvertexdisplacementexplosionquant = 727449
        falbedomapblendalpha = 727976
        bsaccumulatecoloralphamrt2 = 728855
        fprocedural2d1e1 = 729051
        fdeferredlightingdecodeinputlog = 729252
        fbruteforcelighting = 729489
        fbumpnormalmap = 729815
        cbtest = 730009
        bsambientmaskgroup0 = 730463
        fbumpnormalmapblendtransparencymap = 730642
        fprimitivecalcspeculardefault = 730764
        bsblendblendadddestcolorrgb = 731445
        falbedomapblend = 733370
        fshadowfilterpointmulti = 733853
        vs_proceduraltexture = 734173
        tdevelop = 734311
        ia_grass_point = 734499
        fblendfog = 735149
        dsguizwritestencilapply = 735160
        iaskintbnla2wt = 735521
        fdevelopdecode_g = 735858
        fwaterreflection = 735983
        rswireframe = 736173
        cbswing1weight = 736354
        fdistanceattenuation = 736554
        fdistancefogreverseexp2 = 736734
        fvdgetmaskdisable = 736831
        calcprng = 737767
        iadualparaboloid = 737833
        fprimitive2dvirtualscreen = 738234
        bsblendadddestcolor = 738380
        ps_modelfog = 738496
        cbburnemission = 739700
        bsaddcolor = 739998
        fguicalcposition = 740813
        ffresnelschlick2 = 741914
        bsblendminalpha = 742041
        vs_radialblurfilter = 742308
        fdebugviewvertexboneweight = 742570
        rsmeshbias10 = 742662
        vs_adhesionpv = 742924
        ps_systemclearmrt4 = 743763
        cbcubemapfilter = 744154
        tmaterialvelocityedge_nostretch_vs_materialvelocityedge = 744727
        sbpsskinningaddposps_xbox = 745126
        cbambientshadow = 745257
        tssaoreductionnormalmap = 745555
        cbprimitivemetadatalensflare = 745610
        fprimitivecalcposparticle = 746351
        vs_gui_dev = 746711
        fprocedural1d1e1 = 746763
        vs_materialtoonsm = 747052
        ianonskintbnca = 747137
        ffilterlightscatteringmul = 747344
        cbmiragedepthblend = 747517
        cbtattoo = 747826
        iagrasslowest = 748863
        sky_starry_sky_out = 749680
        fhairsh = 751036
        sbidxtoposition = 751576
        fdeferredlightingdecodelineardepth = 751830
        fdeferredlightinglightvolumelightmasktransparent01 = 752587
        fprimitivecalcvolumeblendpsvolume = 753231
        material_output_ex = 753400
        bsainvert = 753770
        dsztestwrite = 753977
        fprojectiontexturecolorg = 754432
        tsoftbodysrctex2 = 755029
        fdistancefogreverseexp = 755175
        fsamplecount8 = 755226
        ianonskintbl = 755422
        fvertexdisplacementdirexplosion = 755490
        fspecular2map = 756743
        twaterbubble = 756884
        cbshadowtype = 756929
        ambient_shadow_out = 757394
        fprimitivecalceye = 757893
        fgrassxzrotate = 758407
        cbviewprojection = 758587
        foutputencodesrgbrgbi = 758793
        tenvmap2 = 759782
        bsaddgwrite = 760343
        fsamplecount24 = 761539
        fwaterrefraction = 761706
        flightmaskrttransparent0 = 761826
        vs_tattoonormalblend2d = 761852
        fshadowreceivelsmrt = 762113
        ia_swing2_high_precision = 762912
        ps_dummydynamicpicker = 763127
        sbsolveedgeconst2ps_xbox = 763173
        radial_blur_output = 763996
        ffisheye = 764061
        ps_lightshaft = 764368
        ffiltercolorcorrecttable = 764801
        fdynamiclightdl7 = 765161
        fmaterialstdalphadefault = 765738
        ffiltergodraysgammacopy = 765746
        fmaterialstdalphareflectvertex = 766003
        tvirtualcubeshadowindirection = 766187
        fjointmatrixexfromcbuf = 766621
        ps_developsimple = 766804
        iaskintb8wt = 767012
        fblendbumpdetailnormalmap = 767877
        fbokehalpha = 767932
        cbskystarryskycolor = 768239
        tattoo_blend2d_output = 768523
        foutputencodedepth24 = 768738
        vs_bloomgaussblur = 768770
        fshadowfilterpoint2 = 769369
        ftexsintan = 769799
        fperpixellightingtoonlmtvs = 769800
        ia_swing = 769864
        ssenvmap = 769891
        fvertexdisplacementmap = 770424
        fanisotropicphongdiffusegmodel = 770508
        ia_builder = 771040
        cbguicolor = 771611
        collision_out = 771624
        fdebugviewpixelbinormal = 771869
        ia_primitive_cloud_billboard = 772091
        sbidxtotexcoord = 772132
        fgrassadjustnormal = 772465
        ia_astral_body = 772517
        tpointlighttexture4 = 772931
        vs_materialstdcafetes = 773456
        fprimitive2dvirtualscreenpanscan = 773725
        fshadowfilter0 = 774525
        flightmasktransparent0 = 775845
        fprimitive2dcalcpospolyline = 776128
        fprimitivecoltexinfluence = 777049
        sbtolocalspaceps = 777318
        fdynamiclocalwind6 = 777427
        ps_systemps3zcullreload = 777458
        fradialfiltersamplecolorscalefade = 777516
        fpointlightr = 777780
        calcpcf2x2 = 778398
        fshadowcastdistance = 778928
        bsaddcolorex = 780463
        fdeferredlightingencodeparameteroverlap = 781538
        getdeveloptexedgefont = 781878
        ps_shadowcasttransparentzoffset = 782033
        primitive_vs_output = 782508
        tyuvdecoderu = 782567
        ia_nonskin_tbnla = 782634
        flocalwindloopdirection = 782870
        adhesion_input = 783371
        flocalwindloopslot0 = 783822
        fshadowfiltermulti = 783843
        ia_grass_outsourcing_f32 = 784119
        fprimitivecalcfog = 784935
        fdeferredlightinglightvolumelightmasksolid01 = 785109
        bsblendmaxalpha = 785784
        frayleighdepthmap = 786748
        ps_gui_polygon = 786881
        fskinningpf8weightbranch = 787036
        fchanneltransparencymap = 787826
        fguicalcuv = 787845
        cbmaterialstdmodeleffect = 788338
        ia_system_copy = 788398
        fmaterialstdspecularmaskexvertexcolorr = 788676
        cbsystemstencilrouting = 790012
        ia_vertex_index_f16 = 790220
        tmaterialstdest = 790814
        gettattooheight = 790918
        fpointlight = 791187
        bsambientmaskgroup1 = 792009
        fswingbillboardtransformfixedy = 792804
        bsmax = 794364
        tvirtualcubeshadowfaceoffset = 794470
        rsmeshbias1 = 795147
        fbokehcompressfactor = 795387
        fgpuparticlelevelcorrectionlinear = 795697
        bsblendaddrgb = 795797
        iavertexindexf16 = 796091
        fwindpoint = 796296
        fswingupdatebillboard = 796413
        fworldcoordinate = 796430
        fmark = 796504
        fdeferredlightinglightvolumelightmaskrtsolid0 = 796706
        tgrassdummy = 796901
        ssdisplacementmap = 797309
        fmorphposition = 797711
        vs_grasslowest = 797775
        falbedo2mapmodulate = 797954
        fprocedural2d1e0 = 798541
        iaskintb2wt = 799218
        vs_waterwposb = 799254
        dsguistencilupdate = 799326
        fdeferredlightingsamplinglightcomformancefiltering = 799613
        sbpsskinningps_xbox = 799886
        cbgrassroot = 800027
        ffogvtflightscattering = 800327
        ffiltergodrays16samplesiterator = 801016
        fprimitivecalctexcoord = 801157
        fsamplecount11 = 801167
        fshadowreceivert1 = 801582
        cbhdrfactor = 801635
        rsprim = 801836
        bsshadowrecvzpass = 802023
        tdetailnormalblendmap = 802295
        bsrevsubalpha = 802916
        iawaterripple = 804412
        fgrassuseposition = 804545
        cbdistortionrefract = 805111
        fddmaterialbump = 805148
        tlightmaskmap = 805230
        fdoffilterdownscale = 805867
        sbcreatedepthnormvs = 806627
        fuvsecondary = 806641
        tgrass = 807767
        tproceduralmap = 808210
        fprocedural1d1e0 = 808349
        ftattoooutput = 808619
        ia_grass_outsourcing = 809592
        ffocclusionfactorfromtexture = 809782
        fprimitivesamplebasemapparalax = 810139
        encoderippleheight = 810406
        ftonemap = 811139
        fisoutofrange = 811202
        vs_heatdepth = 811946
        rsmeshbias11 = 812432
        vs_gui_texture = 812567
        ianonskinba = 812794
        cbgrassglobalwind = 813012
        fuvindirectmap = 813460
        fshadowreceiveattndistance = 814071
        fblendfogdiffuse = 814110
        fddmaterialfinalcombiner = 814579
        ftrianglevertex1 = 814987
        femissionmap = 815520
        fblurmaskfilter = 815787
        ps_deferredlighting_bilateralblurh_size12 = 815876
        fdepthboundstestenable = 816489
        inf_particle_ps_input = 817516
        ps_dof_input = 817709
        fprimitive2dlensflareintensitydefault = 818472
        gs_dof_input = 818782
        ps_reflectiveshadowmap = 819357
        dsztestwritestencilwrite = 819366
        ps_averagecount = 820156
        ia_system_clear = 820252
        iagrassspu = 820997
        fprimitivecalcfogcolor = 821191
        fprimitivecalcntbtessparticle = 821373
        sbtolocalspaceps_xbox = 822143
        calcscreenuvtoviewdepth = 822689
        fshadowfilterpoint3 = 822735
        fcalcuvsecondarydefault = 824044
        ia_nonskin_bc = 824266
        cbguicolorattribute = 824648
        fpervertexshadowfilter8x8 = 825047
        deferred_lighting_light_volume_mrt_ps_output = 825791
        iadevelopprim3d = 826043
        fdynamiclightdl6 = 826495
        flocalwindunroll = 826865
        twatersurfacemap = 827266
        foutlineblendalpha = 827421
        filter_out = 827829
        ssinfparticle = 828263
        ffilteroutlinecomposite = 829580
        fgrassconstraint = 829762
        ssalbedomap = 830073
        fdoffilterpoisson = 830168
        fsamplecount25 = 831061
        flightmaskrttransparent1 = 831348
        ps_systemdepthtoalpha = 831850
        ps_shadowcast = 831922
        fmaterialstdreflectiontypealbedorim = 832002
        bsguiaddcolorrgb = 832207
        fdeferredlightingcompareequallightgroup = 832499
        cboutlinefilter = 832521
        bsblendminalphargb = 832530
        fgpuparticlesamplebasemap = 832549
        vs_gpuparticle = 832865
        tsoftbodysrctex3 = 832963
        fsamplecount9 = 833164
        fdeveloptexcuberefrect = 833221
        ia_swing_high_precision = 833329
        iaskintbnla8wt = 834807
        fwaternormal = 834844
        fintensityweightrgb = 834882
        bsblendcolorrgb = 835266
        iaskintbc1wt = 835436
        creatematerialcontext = 835635
        iasoftbodyquad = 836094
        fguigetvertexcolor = 836107
        fquaternionmultiplay = 836613
        fshadowfilterpointvsm = 836625
        flocalwindloopslot1 = 836952
        convrot = 837001
        cbddmaterialparam = 837259
        cbguifontfilter = 837486
        fwatershadowdisable = 837904
        ia_nonskin_tbnc = 837955
        ps_materialstdlite = 837977
        fwaterbubbleheight = 838234
        iaprimitivesprite = 838772
        fpointlightb = 839248
        fvduvtransform = 839317
        fuvalbedomap = 839405
        talbedomap = 839791
        fdissolvepatterndither = 839964
        fmiragedepthblend = 840640
        grass_spu_input = 840768
        fdebugviewpixeldefault = 840796
        ia_nonskin_tbca = 841250
        fblendratealbedomap = 841278
        ftattoooutputheight = 841772
        sbintegrateps = 842940
        fshadowfilter1 = 844267
        vs_develop2d = 844545
        fuvalbedoburnmap = 844807
        fmaterialstdreflectiontypeprocrim = 845003
        sbiscconstraint = 845053
        fuvtransformoffset2lite = 845275
        flightmasktransparent1 = 845363
        fmaterialstdalbedodefault = 845393
        iasky = 845471
        fgrassxzrotateenable = 845937
        fdeferredlightingcompareequallightgroupdisable = 846243
        cbvertexdisplacementwave = 846607
        ffiltergodrayssourcegraycolor = 846874
        fdynamiclocalwind7 = 846917
        dsdeferredlightingstenciltest = 847306
        fpointlights = 847522
        vs_avglog16 = 847755
        freconstructviewdepthfromdepth = 847836
        bsblendblendadddestcolor = 847974
        getangularattenuation = 848900
        bssubgwrite = 849007
        cbgrasspointshadow = 849167
        tpointlighttexture5 = 850901
        cbwaternormal = 850923
        ffocclusionfactor = 851012
        material_context = 851110
        fgpuparticletonemapnone = 851179
        ps_nvgaussblur = 851735
        diferred_lighting_mrt = 851747
        iasoftbodydecouple = 851783
        cbmiragenoise = 851937
        fpositionrotatequaternion = 852081
        fshadowfilterpcf3x3 = 852557
        ffilteroutlinedirect = 852588
        twaterdetail = 852720
        ps_ambientshadowalpha = 852905
        fyuvdecoder = 853760
        ffilteredgeantialiasingoutputweight = 853913
        ps_dualparaboloid = 853952
        cbdisplacement = 855035
        falphatestgreater = 855091
        tspheremapluttexture = 855634
        fuvtransformoffset2 = 855696
        cbwaterfog = 856121
        finfparticlepos = 856722
        fprimitivecalcnormalmap = 856802
        depthcompare = 857709
        fdeferredlightinglightvolumelightmasktransparent0 = 857751
        fprimitiveuvoffsetdefault = 857798
        fblurdistancemaskenable = 858156
        fwindline = 858438
        ianonskinbl = 858695
        ffiltercolorfogheight = 859091
        ia_miragefilter = 859294
        fuvdisolvemap = 859932
        fcubemapvariancefilterdir = 860318
        fshadowisoutofrangeenable = 860537
        fgrasspervertexshading = 860795
        fddmaterialcalcborderblendrate = 861141
        tprimitive2d = 861785
        tspotlighttexture4 = 861949
        vs_watershadowmap = 862328
        fdynamiceditmaprejectenable = 862529
        fvariancefiltercubeh = 862859
        initmaterialcontext = 862918
        fdeferredlightinggetlightingparameter = 862973
        tsssdiffusemap3 = 863198
        fshadowmultireceivesmoothcascadessmrt = 863651
        ps_deferredlighting_lightvolume_nolighting_lightgroup_mrt = 863708
        fshadowmultireceivesmoothcascadelsmrt = 863728
        fmarkline = 864243
        hs_materialph = 864344
        fvertexdisplacementcurveu = 865078
        foutputencoderrrgbi = 865543
        tnvfilter = 865645
        bsmrtwrite1101 = 866358
        bsaddalpha = 867101
        fvduvsecondary = 867117
        fuvtransformunique = 868412
        iatrianglef16 = 869126
        foutputencodenormal = 869630
        ianonskintbl_la = 869636
        tdetailnormalmap2 = 870036
        sb_psmrtout = 870157
        bscomposite = 870435
        flightmaskshadowmultirt01 = 871045
        gs_gsdoffilter = 871789
        ps_deferredlighting_bilateralblurv_size12 = 872477
        bsssao = 873152
        fwatervolumeblenddisable = 873350
        flowerposydiscardcolormodifier = 873645
        fuvocclusionmap = 873861
        ia_dual_paraboloid = 875197
        finstancingconstantmatrix = 875522
        bsmrtwrite0110 = 876164
        fcafisheye = 876222
        cbsoftbodyrtparam = 876334
        cbshadowcast = 877086
        fprimitivemodelscenesamplerrefractdisplaceuv = 877373
        cbsoftbodydirectgrasswind = 877737
        fprimitivecloudenvdefault = 878003
        fheightfogvtf = 878654
        fdiffuseconstantsrgb = 878728
        ttvnoisemap = 879498
        fsamplecount30 = 879515
        iafilter2 = 879639
        fpervertexlightingvs = 879679
        fvariancefilter = 879963
        tsoftbodytexdepthnorm3 = 880042
        cbvertexdisplacementdirexplosion = 880224
        ssclamppoint = 880550
        fbokehmask = 880784
        tssao = 881417
        tgui = 881526
        fuvtransformsecondary = 882586
        dszwritestencilwrite = 883168
        vs_grass_deferred = 883464
        flightmasksolid01 = 883807
        fprimitivedepthcomparison = 884006
        cbappreflectshadowlight = 884046
        sswraponelinear = 884492
        image_plane_filter_out = 884749
        fdynamiclight6 = 884782
        ttvnoisemaskmap = 884874
        ps_systemclearstencilrouting = 885035
        fsbrand = 885372
        ianonskintb = 885399
        fguicalcpositiondev = 885536
        bsoutlinemodulate = 885867
        iaskintbc8wt = 885987
        iaskintbnla1wt = 886648
        prim_ntb_out = 886832
        ffrontfacenormal = 886964
        fprojectiontexture = 887674
        gs_infparticle = 887954
        tshadowmapcombine = 888251
        feditsimplealbedomapalphamap = 888275
        fssaofilterlineardepthdownscale = 888365
        bsgwrite = 888510
        fpervertexlightingtoonps = 888544
        encodesrgb = 888642
        frimuber = 889120
        flightingdeferredlightingapproximatespecular = 889243
        fbrdfcray = 889298
        foutlinedetectordepthwrap = 889503
        vs_materialoutline = 889508
        primitive_ds_output = 891483
        ps_systemdepthtoalphaaa = 891545
        bsshadowrecvmultitransparentgroup0 = 891699
        fshdiffusedisable = 892605
        tmodelfog = 892720
        fdeferredlightingdecodenormal = 892873
        fshadowlightface1 = 893146
        fswing2weight = 893190
        fshadowreceivefaceattn0 = 893218
        fprocedural2d2e1 = 893314
        fimageblendburn = 893528
        foutputencodesrgb = 894221
        iaskintbn4wt = 894298
        ps_miragesect = 894552
        tshadowmapcombine3 = 894623
        ps_materialhud = 895387
        deferred_lighting_geometry_parameter = 895545
        fmaterialstdspecularcolortypevertexcolor = 896120
        bsblendrevsubrgb = 897117
        ia_develop_prim2d = 897628
        fshadowreceivefaceattndecrease = 898021
        fwaterripple = 898077
        flocalwindloopline = 898112
        iaskinbridge2wt = 899034
        system_depthout = 899774
        tyuvdecodery = 900300
        sb_output2 = 901087
        fdevelopdecode = 901777
        fblendfogprimblend = 901853
        ps_materialsss = 901921
        fbuildersamplebasemap = 902127
        falbedomapblendmaxalpha = 902319
        fgrassperpixellightmask = 903010
        fsamplecount4 = 903729
        cbskyastralbody = 905546
        fsamplecount28 = 905960
        tmaterialvelocityedge_stretch_vs_materialvelocityedge = 906296
        cbmaterialvelocity = 906886
        sbpositiontotexcoordx = 906902
        bsrevsubrgb = 907398
        fchannelspecularmap = 907732
        fprocedural1d2e1 = 908114
        fblend2bumpdetailnormalmap = 908186
        fhairblur = 908729
        fblurdistancemask = 909041
        fintensityweight = 909081
        fdeferredlightingdecodenormalspheremaplut = 909465
        finfparticlecolorlerpblend = 910336
        fskymapoutputselectcloud = 911137
        fcollisionsimpleps = 911727
        ia_softbody_decouple_novtf = 911868
        tprimitive = 911981
        cbappreflect = 912078
        fprimitivemodelsmoothalphadefault = 912306
        fmarkdisable = 912427
        samplelevelvariance = 912541
        cbwaterripple = 914154
        sbintegrateps_xbox = 914470
        vs_sky = 914500
        fdynamiceditmaplyingenable = 915605
        bsguialphamaskadd = 915996
        fgrassinfo = 916249
        fmiragerefract = 916262
        fprimitivecalcdiffuse = 916339
        finfparticletexturepattern = 917025
        bsrevsubblendalphargb = 917306
        twatershadow = 917326
        vs_materialvelocityedge = 917513
        foutlinecompositemultimodulate = 918061
        ftransparencyalphaclip = 918494
        fheightfogdistance = 919027
        tmatrixmap = 919274
        fintensityweightgrayscale = 921017
        hs_dm_constant = 921370
        cbtessellation = 921521
        cbinfparticlecontext = 921877
        fvdgetmaskfromtexture = 922259
        ia_nonskin_tba = 923832
        fdeferredlightingdecodeinput = 924009
        twcvtfprevpos = 924257
        fdeveloptexcubeface = 924597
        fbumpparallaxocclusion = 924799
        ia_water = 924872
        fvertexdisplacementwaverandom = 925409
        ps_skymap = 925958
        fdynamiclight0 = 927003
        cbgrassbillboard = 927557
        fwaterbubblecoordinate = 927740
        ia_nonskin_tbl_la = 927950
        cbgrasscommon = 928088
        ia_skin_tbn_1wt = 928205
        fprimitivetessellateparticle = 928376
        fshadowmultireceivecascadessmrt = 928803
        fshadowmultireceivecascadelsmrt = 928880
        fprimitivemodelscenesampler = 928940
        ps_gui_texture = 929185
        femissionconstant = 931339
        fprimitivecloudcolordefault = 931465
        fdepthtestlt = 931874
        fbokehfarfilter = 932218
        fshadowcastdepth = 934565
        fprimitivecalcshade = 935073
        finstancingmultiply = 935092
        fworldcoordinatesymmetry = 935666
        builder_vs_input = 936104
        sky_map_vs_out = 936385
        vs_gui_polygon = 936567
        fdebugviewpixelnormal = 937127
        fcooktorrancemodel = 937750
        tsky = 938763
        fshadowreceivecascadelsm = 939673
        ps_water = 939675
        sb_ic_output = 939824
        fdebugviewpixelworldnormalmap = 940065
        getscaleoffset = 940373
        ia_filter2 = 940778
        fnvmodelvignetteblend = 941319
        fburnsimplealbedomapburnmap = 941443
        fvertexdisplacementmapdir = 942102
        triangle_input = 942643
        fdebugviewpixelmaskmap = 942995
        fgrassinfowithnormal = 943220
        bsblendrevsubblendcolor = 943240
        system_output = 943577
        ia_skin_bridge_2wt = 943766
        fsystemcachecopycb = 945311
        bsminalpha = 945396
        cbddmaterialparaminnercorrect = 945444
        fsamplecount2 = 945924
        tfogvolumemap = 946436
        fprimitivecalcnormalmapdefault = 946455
        bsguialphamaskwrite = 946805
        tmaterialstddm = 947194
        bsblendaddcolor = 947443
        vs_lightshaft = 947725
        fwaterbubblemapmask = 947872
        vs_materialvelocity2 = 947902
        ps_grassshadowdummy = 948227
        ffiltergodraysthreshold = 948670
        fmiragedepthblenddefault = 948745
        twcvtfpos1 = 950667
        ffilteroutlinecompositeemit = 950850
        ffiltergodrayssourcecolor = 950954
        tspotlighttexture2 = 951240
        setuplight = 951344
        cbbruteforcelightingparam = 951444
        ps_systemtonemap = 952026
        textendmap = 952550
        ps_adhesionpv = 952785
        fsystemmakemiplevel = 952852
        iagrasshicomp2 = 952966
        calcviewdepth = 953633
        vs_modelfog = 953987
        tsssdiffusemap5 = 954091
        fprimitivecalcntb = 954592
        deferred_lighting_gbuffer_pass_vs_output = 954604
        ffinalcombiner = 955050
        ps_cubicblur = 955608
        hs_materialpn = 955757
        fprimitive2dcalcposlensflare = 956270
        ffogvtfdistanceest = 956274
        cbssaoffilter = 956375
        world_coordinate_input = 956433
        ia_nonskin_tbnl_la = 956652
        fcalcprimarycolortoonvertexcolor = 957315
        sbcapsuleconstraint = 957356
        sbnormalpackf32 = 958017
        sampledepth = 958148
        bsmultiplycoloralphamrt2 = 958351
        ia_gui = 958613
        flightmask = 958892
        cbdynamiclighting = 960145
        fvertexdisplacementdirexplosionplus = 960904
        dsdefault = 961346
        fprimitiveocclusionfactordefault = 961494
        fprimitivemodelscenesamplerrefractalpha = 961945
        foutlinefade = 962043
        bsinvcomposite = 962574
        cbmiragecommon = 962615
        ttextureblendmap = 962661
        getdeveloptexcuberefrect = 962896
        tcolorcorrecttablemap = 962936
        fuvindirect = 963292
        fdeferredlightinggetclearcolorlightbufferlog = 963525
        vs_nvgaussblur = 963745
        ps_shadowcasttransparent = 963753
        calcpcf3x3 = 965183
        fprocedural2d4e3 = 965660
        fprimitiveocclusionfactorps = 966163
        fdebugviewvertexbonenum = 966450
        fgrassshadingdisable = 966495
        fuvindirectmask = 966695
        fgrassusepointposition = 966778
        fsbrand2 = 966933
        ftonemapexposureex = 967112
        bsmaxalpha = 967445
        ps_builder = 967859
        fskycorrecthorizondisable = 968135
        fgrassmaterialnormal = 968309
        ps_systemdepthdownsample = 968335
        fprocedural1d4e3 = 968396
        tsoftbodytexdepthnorm5 = 968863
        ftonemapreinhard = 969480
        tmiragerefractionmap = 969898
        foutlineblend = 970137
        iaprimitivecloud = 970793
        fshadowreceivesmoothcascadessmlite = 971268
        bsblendblendadddestalphargb = 971348
        bsoutlineblend = 971849
        fdeferredlightinggetclearcolorlightbuffer = 972257
        tnormalblendmap = 972478
        fmiragesamplescene = 972583
        deferred_material_ps_output = 972702
        ps_grasspointmap = 972787
        ssdisolvemap = 972837
        temissionmap = 973115
        fshadowdepthbias = 973198
        spreadcompare = 973276
        fldtexturesampler3xbox = 973426
        dsoutlinezteststenciltest = 973676
        fbumpdetailmasknormalu_vmap = 973821
        fshadowreceiveattnspot = 973963
        tsoftbody = 975578
        ps_systemcopy = 975657
        falbedomap2 = 975684
        bsguialphamaskupdate = 976427
        tfogtable = 976467
        fprimitiveocclusionlensflare = 976950
        ps_fxaa3 = 976985
        ps_cloudprimitive = 977513
        fvduvunique = 977526
        fmaterialstdreflectiontypeextendrim = 977547
        fprimitivecalcntbpolyline = 977565
        calcparticlerotation = 977663
        tprocedural2d0 = 977672
        tdepthbiasmap = 977873
        ia_skin_tbc_1wt = 978300
        fblendspecularmap = 978429
        fbumpparallax = 979831
        fgrassuvswitch = 980022
        sbsolveconstiscps_xbox = 980047
        fgsdofcopy = 980255
        ia_skin_tb_4wt = 980347
        ia_nonskin_bca = 980539
        ffiltercolorcorrectvolumeinterpolate = 980820
        sstransparencymap = 980839
        tgrassoutsourceing = 981396
        fshadowisoutofrange0 = 981503
        fgpuparticletonemap = 981923
        iaskinvelocytyedge = 982036
        cbdistortion = 982179
        ps_gpuparticle = 982743
        tdsfbuffer = 983137
        ffoglightscattering = 983201
        tcollision = 984072
        fdamagebumpdetailnormalmap = 984287
        fskinning8weight = 984426
        frotationnormalfromquaternion = 984623
        ffilteredgeantialiasing = 984992
        fwaterdetailworldcoodinate = 985364
        fsamplecount23 = 985952
        tbuilderbasemap = 986046
        ps_bloomgaussblur = 986122
        vs_gui_blend = 987209
        cbssaoffilterlineardepth = 987322
        tsoftbodysrctex5 = 987382
        cbwatershadow = 987426
        ia_skin_tbn_8wt = 987714
        ssradialfilterclamplinear = 988234
        ia_triangle_index_f16 = 989274
        fnvfinalcombiner = 989338
        fprimitivecalcvolumeblendpsinvvolume = 989440
        fmaterialvlocityinflate = 989533
        fwaterripplefrustum = 990173
        fwaterdetailtexturecoodinate = 990302
        twaterripple = 990342
        trecalcnormal = 990410
        fguitexturesampling = 990463
        tglobalenvmap = 990590
        cbmiragerefract = 991001
        fmaterialstdspecularcolortypedefault = 991303
        fdamagesimplealbedomapalphamap = 991585
        flocalwindlooppoint = 992016
        getastralscattering = 993516
        tlogaverage = 993751
        fshadowreceivepoint = 994192
        fshadowfilterpointpcf3x3 = 994993
        getrayleighscatter = 995510
        fburnalbedomapburnmap = 996025
        water_output = 996120
        bsmrtwrite0010 = 996531
        ttvnoisefilter = 996583
        fshadowreceivecascadevlsm = 996594
        iaswinghighprecision = 996991
        frsmgatherindirectlightinghighquality = 997258
        ps_bloomextraction = 997676
        fdynamiclightdl0 = 997706
        fdeferredlightinglightvolumelightmasktransparentfullsize = 998491
        fgpuparticlefogvsalpha = 998983
        fprimitivecalcspecular = 999637
        fdeferredlightingencodeoutputlog = 999991
        ftrianglevertexselector = 1000478
        flightmasksolid0 = 1000832
        fshadowfilterpoint = 1000898
        fbumphair = 1001136
        tmaterialstdcafetes = 1001146
        fprimitivemaskmapparallax = 1001176
        fwaterdetailnormalmulti = 1001192
        fcalcuvsecondaryspheremap = 1001591
        fdynamiclocalwind1 = 1001840
        fssaobounce = 1002088
        simwater_for_view_vs_output = 1002204
        light_output = 1003412
        dsguizwritestencilapplyreverse = 1003714
        ssshadowvariance1 = 1003803
        bsmrtwrite1001 = 1004033
        creatematerialcontextex = 1004994
        foutlinecompositemodulate = 1005139
        fwatershadow = 1005525
        foutlinedetector0 = 1005991
        fskinning2weight = 1006116
        ffogvtfdistancetableest = 1006154
        ffiltergodraysalpha = 1006892
        tpointlighttexture3 = 1007328
        fuvextendmapprimary = 1008078
        ia_nonskin_tbl = 1008645
        tprocedural1d1 = 1009095
        fshadowattenuation = 1009172
        ps_systemdownsample4 = 1009811
        fpointlightd = 1010533
        fdistancefogexp2 = 1011335
        fburnemissionmapblend = 1011401
        fguicalcuvwrap = 1011426
        fskinning4weight = 1011486
        fdistancefogexp = 1012578
        fmaterialstdspecularmaskalbedo = 1012686
        fuvscreen = 1013078
        fradialbluralpha = 1013599
        ssenvmaplodbias1 = 1013650
        ps_nvdownsample4 = 1013826
        fprimitiveuvclamp = 1014629
        fdissolvetexture = 1015709
        cbprimitiveex = 1015931
        falbedomapadd = 1016134
        fnvmodeldiscard = 1016162
        toonvertexcolordisable = 1016644
        ffilterfogtable = 1016866
        rsmeshbias7 = 1017662
        foutputencodezero = 1017681
        fwatervolumeblend = 1017855
        fmaterialstdalbedoprocmodulate = 1018272
        ia_water_vcolor = 1018452
        fguicalcpositiondev3d = 1018764
        ps_systemdownsample16 = 1018954
        fdepthboundstest = 1019205
        fambientshadowimage = 1019211
        cbvolumecolorcorrectblend = 1019590
        cbroptest = 1020097
        fdiffusevertexcolorocclusion = 1020155
        cbinstanceshadowcastercache = 1020548
        ttextureblendsourcecube1 = 1020562
        fdirectionalwind = 1020656
        ps_systemminidepthcopy = 1020900
        deconstructvelocity = 1020978
        fdistancefoglinear = 1021097
        fgpuparticlecalcdepthblend = 1021218
        ps_vertexoutput = 1021530
        sbsphereconstraint = 1022028
        fprimitive2dvirtualscreenfullscreen = 1022293
        fprimitivescenesamplerrefract = 1022593
        hs_phtrianglesconstant = 1022656
        fbrdfhairhalflambert = 1022906
        fsamplecount17 = 1023162
        ps_imageplanefiltercubeex = 1023579
        tgbuffer = 1024108
        ps_vignetteextraction = 1024225
        iatextureblend = 1024821
        tssaowidemap = 1026094
        bsblendrevsubblendcolorrgb = 1026977
        rsscissorprim = 1027168
        sblodtransps = 1027391
        fbrdfdeferredlighting = 1028062
        fprimitivecalcdepthblend = 1028293
        fprocedural1d3e1 = 1028453
        fmarkpoint = 1028541
        tsoftbodytexdepthnorm8 = 1029154
        nulllighttexture = 1030142
        sbtexcoordtopositiony = 1030508
        ps_systemaacopy = 1031306
        dsguiztestwritestencilapplyreverse = 1031650
        vs_grasspointmap = 1031703
        frsmgatherindirectlighting = 1032014
        fshadowreceiveattn1 = 1032192
        fcalcprimarycolorstdlitedefault = 1032204
        fmaterialstdvertexcolorshadowenable = 1032288
        finfparticlecalctexcoord = 1032808
        sssystemcopy = 1033842
        foutlinedetector = 1033940
        iagui = 1033954
        iacollisioninput = 1034238
        tvnoise_filter_output = 1034683
        finfparticlecolorconstantblend = 1034947
        fprocedural2d3e1 = 1035189
        ps_systemclearmrt3 = 1035504
        hs_dmtrianglesconstant = 1035727
        fpointlightbr = 1035746
        updatedensity = 1035764
        fshininessmap = 1036259
        ps_materialtoonsm = 1036580
        fskymapbeginendcloud = 1036600
        ffiltercopycolor = 1037220
        vs_grass = 1037365
        fprimitiveclipdefault = 1037802
        cbmaterialconstant = 1037815
        ssgui = 1038037
        ia_skin_tbc_8wt = 1038067
        fguicalccolorscalingon = 1038470
        fmaterialstdalbedoextendalphablend = 1039200
        fdiffuse = 1039215
        fbilateralfilterh = 1039736
        ps_dummypicker1 = 1039777
        cbdoffilter = 1040353
        fprimitivevsalphaclip = 1040784
        fjointmatrixpffromcbuf = 1041265
        shadowreceive_output = 1041323
        getdepthcolumn8 = 1041728
        fdiffuseconstant = 1041806
        fprimitiveclip = 1041951
        fluminanceenable = 1042503
        fgpuparticlecalctexcoorddefault = 1042941
        fprimitivecalcdepthblenddefault = 1043573
        cbwaterdetail = 1043612
        fambient = 1044438
        fbrdfgrassdiffuse = 1044459
        fswingbillboardtransform = 1044698
        freconstructviewdepthfromlineardepth = 1044866
        fshaderattributes = 1045031
        fshadowreceivefaceattnincrease = 1045198
        fcalcprimarycolorconstantlitevertex = 1045839
        talbedoblendmap = 1045950
        bsblendrevsubcolor = 1046425
        ia_gpu_particle = 1046781
        fbump = 1047504
        fdoffilterlight2 = 1047799
        cbshadowreceive0 = 1048082
        fgrassbillboardposition = 1048090
        fsystemcopygamma = 1048350
    def __init__(self, app_id, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self.app_id = app_id

    def _read(self):
        self.id_magic = self._io.read_bytes(4)
        if not (self.id_magic == b"\x4D\x52\x4C\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x52\x4C\x00", self.id_magic, self._io, u"/seq/0")
        self.version = self._io.read_u4le()
        self.num_materials = self._io.read_u4le()
        self.num_textures = self._io.read_u4le()
        self.shader_version = self._io.read_u4le()
        self.ofs_textures = self._io.read_u4le()
        self.ofs_materials = self._io.read_u4le()
        self.textures = []
        for i in range(self.num_textures):
            _t_textures = Mrl.TextureSlot(self._io, self, self._root)
            _t_textures._read()
            self.textures.append(_t_textures)

        self.materials = []
        for i in range(self.num_materials):
            _t_materials = Mrl.Material(self._io, self, self._root)
            _t_materials._read()
            self.materials.append(_t_materials)



    def _fetch_instances(self):
        pass
        for i in range(len(self.textures)):
            pass
            self.textures[i]._fetch_instances()

        for i in range(len(self.materials)):
            pass
            self.materials[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Mrl, self)._write__seq(io)
        self._io.write_bytes(self.id_magic)
        self._io.write_u4le(self.version)
        self._io.write_u4le(self.num_materials)
        self._io.write_u4le(self.num_textures)
        self._io.write_u4le(self.shader_version)
        self._io.write_u4le(self.ofs_textures)
        self._io.write_u4le(self.ofs_materials)
        for i in range(len(self.textures)):
            pass
            self.textures[i]._write__seq(self._io)

        for i in range(len(self.materials)):
            pass
            self.materials[i]._write__seq(self._io)



    def _check(self):
        pass
        if (len(self.id_magic) != 4):
            raise kaitaistruct.ConsistencyError(u"id_magic", len(self.id_magic), 4)
        if not (self.id_magic == b"\x4D\x52\x4C\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x4D\x52\x4C\x00", self.id_magic, None, u"/seq/0")
        if (len(self.textures) != self.num_textures):
            raise kaitaistruct.ConsistencyError(u"textures", len(self.textures), self.num_textures)
        for i in range(len(self.textures)):
            pass
            if self.textures[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"textures", self.textures[i]._root, self._root)
            if self.textures[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"textures", self.textures[i]._parent, self)

        if (len(self.materials) != self.num_materials):
            raise kaitaistruct.ConsistencyError(u"materials", len(self.materials), self.num_materials)
        for i in range(len(self.materials)):
            pass
            if self.materials[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._root, self._root)
            if self.materials[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._parent, self)


    class AnimSubEntry1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                _t_values = Mrl.AnimType1(self._io, self, self._root)
                _t_values._read()
                self.values.append(_t_values)



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass
                self.values[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry1, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self.values[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.header) != 4):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 4)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != self._parent.info.num_entry):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), self._parent.info.num_entry)
            for i in range(len(self.values)):
                pass
                if self.values[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._root, self._root)
                if self.values[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._parent, self)



    class CbMaterial(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re0":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev2":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbMaterial, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev1":
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re0":
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev2":
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbMaterial1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re0":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev2":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"re1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re0":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev2":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbGlobals1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = []
            for i in range(3):
                self.f_parallax_max_sample.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(4):
                self.f_light_map_color.append(self._io.read_f4le())

            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_screen_uv_scale = []
            for i in range(2):
                self.f_screen_uv_scale.append(self._io.read_f4le())

            self.f_screen_uv_offset = []
            for i in range(2):
                self.f_screen_uv_offset.append(self._io.read_f4le())

            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(3):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_emission_threshold = self._io.read_f4le()
            self.f_constant_color = []
            for i in range(4):
                self.f_constant_color.append(self._io.read_f4le())

            self.f_roughness = self._io.read_f4le()
            self.f_roughness_rgb = []
            for i in range(3):
                self.f_roughness_rgb.append(self._io.read_f4le())

            self.f_anisotoropic_direction = []
            for i in range(3):
                self.f_anisotoropic_direction.append(self._io.read_f4le())

            self.f_smoothness = self._io.read_f4le()
            self.f_anistropic_uv = []
            for i in range(2):
                self.f_anistropic_uv.append(self._io.read_f4le())

            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.f_primary_color = []
            for i in range(4):
                self.f_primary_color.append(self._io.read_f4le())

            self.f_secondary_color = []
            for i in range(4):
                self.f_secondary_color.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_albedo_color)):
                pass

            for i in range(len(self.f_albedo_blend_color)):
                pass

            for i in range(len(self.f_parallax_max_sample)):
                pass

            for i in range(len(self.f_light_map_color)):
                pass

            for i in range(len(self.f_thin_map_color)):
                pass

            for i in range(len(self.f_screen_uv_scale)):
                pass

            for i in range(len(self.f_screen_uv_offset)):
                pass

            for i in range(len(self.f_indirect_offset)):
                pass

            for i in range(len(self.f_indirect_scale)):
                pass

            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            for i in range(len(self.f_specular_color)):
                pass

            for i in range(len(self.f_emission_color)):
                pass

            for i in range(len(self.f_constant_color)):
                pass

            for i in range(len(self.f_roughness_rgb)):
                pass

            for i in range(len(self.f_anisotoropic_direction)):
                pass

            for i in range(len(self.f_anistropic_uv)):
                pass

            for i in range(len(self.f_primary_color)):
                pass

            for i in range(len(self.f_secondary_color)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbGlobals1, self)._write__seq(io)
            self._io.write_f4le(self.f_alpha_clip_threshold)
            for i in range(len(self.f_albedo_color)):
                pass
                self._io.write_f4le(self.f_albedo_color[i])

            for i in range(len(self.f_albedo_blend_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend_color[i])

            self._io.write_f4le(self.f_detail_normal_power)
            self._io.write_f4le(self.f_detail_normal_uv_scale)
            self._io.write_f4le(self.f_detail_normal2_power)
            self._io.write_f4le(self.f_detail_normal2_uv_scale)
            self._io.write_f4le(self.f_primary_shift)
            self._io.write_f4le(self.f_secondary_shift)
            self._io.write_f4le(self.f_parallax_factor)
            self._io.write_f4le(self.f_parallax_self_occlusion)
            self._io.write_f4le(self.f_parallax_min_sample)
            for i in range(len(self.f_parallax_max_sample)):
                pass
                self._io.write_f4le(self.f_parallax_max_sample[i])

            for i in range(len(self.f_light_map_color)):
                pass
                self._io.write_f4le(self.f_light_map_color[i])

            for i in range(len(self.f_thin_map_color)):
                pass
                self._io.write_f4le(self.f_thin_map_color[i])

            self._io.write_f4le(self.f_thin_scattering)
            for i in range(len(self.f_screen_uv_scale)):
                pass
                self._io.write_f4le(self.f_screen_uv_scale[i])

            for i in range(len(self.f_screen_uv_offset)):
                pass
                self._io.write_f4le(self.f_screen_uv_offset[i])

            for i in range(len(self.f_indirect_offset)):
                pass
                self._io.write_f4le(self.f_indirect_offset[i])

            for i in range(len(self.f_indirect_scale)):
                pass
                self._io.write_f4le(self.f_indirect_scale[i])

            self._io.write_f4le(self.f_fresnel_schlick)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass
                self._io.write_f4le(self.f_fresnel_schlick_rgb[i])

            for i in range(len(self.f_specular_color)):
                pass
                self._io.write_f4le(self.f_specular_color[i])

            self._io.write_f4le(self.f_shininess)
            for i in range(len(self.f_emission_color)):
                pass
                self._io.write_f4le(self.f_emission_color[i])

            self._io.write_f4le(self.f_emission_threshold)
            for i in range(len(self.f_constant_color)):
                pass
                self._io.write_f4le(self.f_constant_color[i])

            self._io.write_f4le(self.f_roughness)
            for i in range(len(self.f_roughness_rgb)):
                pass
                self._io.write_f4le(self.f_roughness_rgb[i])

            for i in range(len(self.f_anisotoropic_direction)):
                pass
                self._io.write_f4le(self.f_anisotoropic_direction[i])

            self._io.write_f4le(self.f_smoothness)
            for i in range(len(self.f_anistropic_uv)):
                pass
                self._io.write_f4le(self.f_anistropic_uv[i])

            self._io.write_f4le(self.f_primary_expo)
            self._io.write_f4le(self.f_secondary_expo)
            for i in range(len(self.f_primary_color)):
                pass
                self._io.write_f4le(self.f_primary_color[i])

            for i in range(len(self.f_secondary_color)):
                pass
                self._io.write_f4le(self.f_secondary_color[i])



        def _check(self):
            pass
            if (len(self.f_albedo_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color", len(self.f_albedo_color), 3)
            for i in range(len(self.f_albedo_color)):
                pass

            if (len(self.f_albedo_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend_color", len(self.f_albedo_blend_color), 4)
            for i in range(len(self.f_albedo_blend_color)):
                pass

            if (len(self.f_parallax_max_sample) != 3):
                raise kaitaistruct.ConsistencyError(u"f_parallax_max_sample", len(self.f_parallax_max_sample), 3)
            for i in range(len(self.f_parallax_max_sample)):
                pass

            if (len(self.f_light_map_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_light_map_color", len(self.f_light_map_color), 4)
            for i in range(len(self.f_light_map_color)):
                pass

            if (len(self.f_thin_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_thin_map_color", len(self.f_thin_map_color), 3)
            for i in range(len(self.f_thin_map_color)):
                pass

            if (len(self.f_screen_uv_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_screen_uv_scale", len(self.f_screen_uv_scale), 2)
            for i in range(len(self.f_screen_uv_scale)):
                pass

            if (len(self.f_screen_uv_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_screen_uv_offset", len(self.f_screen_uv_offset), 2)
            for i in range(len(self.f_screen_uv_offset)):
                pass

            if (len(self.f_indirect_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_offset", len(self.f_indirect_offset), 2)
            for i in range(len(self.f_indirect_offset)):
                pass

            if (len(self.f_indirect_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_scale", len(self.f_indirect_scale), 2)
            for i in range(len(self.f_indirect_scale)):
                pass

            if (len(self.f_fresnel_schlick_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_fresnel_schlick_rgb", len(self.f_fresnel_schlick_rgb), 3)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            if (len(self.f_specular_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color", len(self.f_specular_color), 3)
            for i in range(len(self.f_specular_color)):
                pass

            if (len(self.f_emission_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_emission_color", len(self.f_emission_color), 3)
            for i in range(len(self.f_emission_color)):
                pass

            if (len(self.f_constant_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_constant_color", len(self.f_constant_color), 4)
            for i in range(len(self.f_constant_color)):
                pass

            if (len(self.f_roughness_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_roughness_rgb", len(self.f_roughness_rgb), 3)
            for i in range(len(self.f_roughness_rgb)):
                pass

            if (len(self.f_anisotoropic_direction) != 3):
                raise kaitaistruct.ConsistencyError(u"f_anisotoropic_direction", len(self.f_anisotoropic_direction), 3)
            for i in range(len(self.f_anisotoropic_direction)):
                pass

            if (len(self.f_anistropic_uv) != 2):
                raise kaitaistruct.ConsistencyError(u"f_anistropic_uv", len(self.f_anistropic_uv), 2)
            for i in range(len(self.f_anistropic_uv)):
                pass

            if (len(self.f_primary_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_primary_color", len(self.f_primary_color), 4)
            for i in range(len(self.f_primary_color)):
                pass

            if (len(self.f_secondary_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_secondary_color", len(self.f_secondary_color), 4)
            for i in range(len(self.f_secondary_color)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 288
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimSubEntry5(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry5, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self._io.write_u1(self.values[i])



        def _check(self):
            pass
            if (len(self.header) != 12):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 12)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != (8 * self._parent.info.num_entry)):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), (8 * self._parent.info.num_entry))
            for i in range(len(self.values)):
                pass



    class CmdTexIdx(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.tex_idx = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.CmdTexIdx, self)._write__seq(io)
            self._io.write_u4le(self.tex_idx)


        def _check(self):
            pass


    class CbColorMask(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"re6":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev2":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbColorMask, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re6":
                pass
                self._m_app_specific = Mrl.CbColorMask1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev2":
                pass
                self._m_app_specific = Mrl.CbColorMask1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbColorMask1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re6":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev2":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"re6":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev2":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbVertexDisplacement(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re6":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re0":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev2":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbVertexDisplacement, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev1":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re6":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re0":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev2":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re6":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re0":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev2":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"re1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re6":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re0":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev2":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class AnimInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk = self._io.read_bits_int_le(2)
            self.num_entry2 = self._io.read_bits_int_le(16)
            self.num_entry1 = self._io.read_bits_int_le(14)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.AnimInfo, self)._write__seq(io)
            self._io.write_bits_int_le(2, self.unk)
            self._io.write_bits_int_le(16, self.num_entry2)
            self._io.write_bits_int_le(14, self.num_entry1)


        def _check(self):
            pass


    class AnimType4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = []
            for i in range(19):
                self.unk_01.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_01)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimType4, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            for i in range(len(self.unk_01)):
                pass
                self._io.write_f4le(self.unk_01[i])



        def _check(self):
            pass
            if (len(self.unk_01) != 19):
                raise kaitaistruct.ConsistencyError(u"unk_01", len(self.unk_01), 19)
            for i in range(len(self.unk_01)):
                pass



    class CbOutlineEx(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbOutlineEx, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbOutlineEx1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbOutlineEx1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class ShaderObject(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.index = self._io.read_bits_int_le(12)
            self.name_hash = KaitaiStream.resolve_enum(Mrl.ShaderObjectHash, self._io.read_bits_int_le(20))


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.ShaderObject, self)._write__seq(io)
            self._io.write_bits_int_le(12, self.index)
            self._io.write_bits_int_le(20, int(self.name_hash))


        def _check(self):
            pass


    class CbVertexDisplacement21(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_vtx_disp_start2 = self._io.read_f4le()
            self.f_vtx_disp_scale2 = self._io.read_f4le()
            self.f_vtx_disp_inv_area2 = self._io.read_f4le()
            self.f_vtx_disp_rcn2 = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.CbVertexDisplacement21, self)._write__seq(io)
            self._io.write_f4le(self.f_vtx_disp_start2)
            self._io.write_f4le(self.f_vtx_disp_scale2)
            self._io.write_f4le(self.f_vtx_disp_inv_area2)
            self._io.write_f4le(self.f_vtx_disp_rcn2)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbGlobals(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re6":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re0":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev2":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbGlobals, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self._m_app_specific = Mrl.CbGlobals1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev1":
                pass
                self._m_app_specific = Mrl.CbGlobals1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re6":
                pass
                self._m_app_specific = Mrl.CbGlobals3(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re0":
                pass
                self._m_app_specific = Mrl.CbGlobals1(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbGlobals4(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev2":
                pass
                self._m_app_specific = Mrl.CbGlobals2(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbGlobals1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re6":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re0":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev2":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"re1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re6":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re0":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev2":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbSpecularBlend1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_specular_blend_color = []
            for i in range(4):
                self.f_specular_blend_color.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_specular_blend_color)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbSpecularBlend1, self)._write__seq(io)
            for i in range(len(self.f_specular_blend_color)):
                pass
                self._io.write_f4le(self.f_specular_blend_color[i])



        def _check(self):
            pass
            if (len(self.f_specular_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_specular_blend_color", len(self.f_specular_blend_color), 4)
            for i in range(len(self.f_specular_blend_color)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbMaterial1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_diffuse_color = []
            for i in range(3):
                self.f_diffuse_color.append(self._io.read_f4le())

            self.f_transparency = self._io.read_f4le()
            self.f_reflective_color = []
            for i in range(3):
                self.f_reflective_color.append(self._io.read_f4le())

            self.f_transparency_volume = self._io.read_f4le()
            self.f_uv_transform = []
            for i in range(8):
                self.f_uv_transform.append(self._io.read_f4le())

            self.f_uv_transform2 = []
            for i in range(8):
                self.f_uv_transform2.append(self._io.read_f4le())

            self.f_uv_transform3 = []
            for i in range(8):
                self.f_uv_transform3.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_diffuse_color)):
                pass

            for i in range(len(self.f_reflective_color)):
                pass

            for i in range(len(self.f_uv_transform)):
                pass

            for i in range(len(self.f_uv_transform2)):
                pass

            for i in range(len(self.f_uv_transform3)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbMaterial1, self)._write__seq(io)
            for i in range(len(self.f_diffuse_color)):
                pass
                self._io.write_f4le(self.f_diffuse_color[i])

            self._io.write_f4le(self.f_transparency)
            for i in range(len(self.f_reflective_color)):
                pass
                self._io.write_f4le(self.f_reflective_color[i])

            self._io.write_f4le(self.f_transparency_volume)
            for i in range(len(self.f_uv_transform)):
                pass
                self._io.write_f4le(self.f_uv_transform[i])

            for i in range(len(self.f_uv_transform2)):
                pass
                self._io.write_f4le(self.f_uv_transform2[i])

            for i in range(len(self.f_uv_transform3)):
                pass
                self._io.write_f4le(self.f_uv_transform3[i])



        def _check(self):
            pass
            if (len(self.f_diffuse_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_diffuse_color", len(self.f_diffuse_color), 3)
            for i in range(len(self.f_diffuse_color)):
                pass

            if (len(self.f_reflective_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_reflective_color", len(self.f_reflective_color), 3)
            for i in range(len(self.f_reflective_color)):
                pass

            if (len(self.f_uv_transform) != 8):
                raise kaitaistruct.ConsistencyError(u"f_uv_transform", len(self.f_uv_transform), 8)
            for i in range(len(self.f_uv_transform)):
                pass

            if (len(self.f_uv_transform2) != 8):
                raise kaitaistruct.ConsistencyError(u"f_uv_transform2", len(self.f_uv_transform2), 8)
            for i in range(len(self.f_uv_transform2)):
                pass

            if (len(self.f_uv_transform3) != 8):
                raise kaitaistruct.ConsistencyError(u"f_uv_transform3", len(self.f_uv_transform3), 8)
            for i in range(len(self.f_uv_transform3)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 128
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbAppReflect1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_app_water_reflect_scale = self._io.read_f4le()
            self.f_app_shadow_light_scale = self._io.read_f4le()
            self.padding = []
            for i in range(2):
                self.padding.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.padding)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbAppReflect1, self)._write__seq(io)
            self._io.write_f4le(self.f_app_water_reflect_scale)
            self._io.write_f4le(self.f_app_shadow_light_scale)
            for i in range(len(self.padding)):
                pass
                self._io.write_f4le(self.padding[i])



        def _check(self):
            pass
            if (len(self.padding) != 2):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 2)
            for i in range(len(self.padding)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbAppReflect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbAppReflect, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbAppReflect1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbAppReflect1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbGlobals4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.padding_1 = self._io.read_f4le()
            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = self._io.read_f4le()
            self.padding_2 = []
            for i in range(2):
                self.padding_2.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(3):
                self.f_light_map_color.append(self._io.read_f4le())

            self.padding_3 = self._io.read_f4le()
            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(3):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_roughness = self._io.read_f4le()
            self.f_roughness_rgb = []
            for i in range(3):
                self.f_roughness_rgb.append(self._io.read_f4le())

            self.f_anisotoropic_direction = []
            for i in range(3):
                self.f_anisotoropic_direction.append(self._io.read_f4le())

            self.f_smoothness = self._io.read_f4le()
            self.f_anistropic_uv = []
            for i in range(2):
                self.f_anistropic_uv.append(self._io.read_f4le())

            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.f_primary_color = []
            for i in range(3):
                self.f_primary_color.append(self._io.read_f4le())

            self.padding_4 = self._io.read_f4le()
            self.f_secondary_color = []
            for i in range(3):
                self.f_secondary_color.append(self._io.read_f4le())

            self.padding_5 = self._io.read_f4le()
            self.xyzw_sepalate = []
            for i in range(16):
                self.xyzw_sepalate.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_albedo_color)):
                pass

            for i in range(len(self.f_albedo_blend_color)):
                pass

            for i in range(len(self.padding_2)):
                pass

            for i in range(len(self.f_light_map_color)):
                pass

            for i in range(len(self.f_thin_map_color)):
                pass

            for i in range(len(self.f_indirect_offset)):
                pass

            for i in range(len(self.f_indirect_scale)):
                pass

            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            for i in range(len(self.f_specular_color)):
                pass

            for i in range(len(self.f_emission_color)):
                pass

            for i in range(len(self.f_roughness_rgb)):
                pass

            for i in range(len(self.f_anisotoropic_direction)):
                pass

            for i in range(len(self.f_anistropic_uv)):
                pass

            for i in range(len(self.f_primary_color)):
                pass

            for i in range(len(self.f_secondary_color)):
                pass

            for i in range(len(self.xyzw_sepalate)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbGlobals4, self)._write__seq(io)
            for i in range(len(self.f_albedo_color)):
                pass
                self._io.write_f4le(self.f_albedo_color[i])

            self._io.write_f4le(self.padding_1)
            for i in range(len(self.f_albedo_blend_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend_color[i])

            self._io.write_f4le(self.f_detail_normal_power)
            self._io.write_f4le(self.f_detail_normal_uv_scale)
            self._io.write_f4le(self.f_detail_normal2_power)
            self._io.write_f4le(self.f_detail_normal2_uv_scale)
            self._io.write_f4le(self.f_primary_shift)
            self._io.write_f4le(self.f_secondary_shift)
            self._io.write_f4le(self.f_parallax_factor)
            self._io.write_f4le(self.f_parallax_self_occlusion)
            self._io.write_f4le(self.f_parallax_min_sample)
            self._io.write_f4le(self.f_parallax_max_sample)
            for i in range(len(self.padding_2)):
                pass
                self._io.write_f4le(self.padding_2[i])

            for i in range(len(self.f_light_map_color)):
                pass
                self._io.write_f4le(self.f_light_map_color[i])

            self._io.write_f4le(self.padding_3)
            for i in range(len(self.f_thin_map_color)):
                pass
                self._io.write_f4le(self.f_thin_map_color[i])

            self._io.write_f4le(self.f_thin_scattering)
            for i in range(len(self.f_indirect_offset)):
                pass
                self._io.write_f4le(self.f_indirect_offset[i])

            for i in range(len(self.f_indirect_scale)):
                pass
                self._io.write_f4le(self.f_indirect_scale[i])

            self._io.write_f4le(self.f_fresnel_schlick)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass
                self._io.write_f4le(self.f_fresnel_schlick_rgb[i])

            for i in range(len(self.f_specular_color)):
                pass
                self._io.write_f4le(self.f_specular_color[i])

            self._io.write_f4le(self.f_shininess)
            for i in range(len(self.f_emission_color)):
                pass
                self._io.write_f4le(self.f_emission_color[i])

            self._io.write_f4le(self.f_alpha_clip_threshold)
            self._io.write_f4le(self.f_roughness)
            for i in range(len(self.f_roughness_rgb)):
                pass
                self._io.write_f4le(self.f_roughness_rgb[i])

            for i in range(len(self.f_anisotoropic_direction)):
                pass
                self._io.write_f4le(self.f_anisotoropic_direction[i])

            self._io.write_f4le(self.f_smoothness)
            for i in range(len(self.f_anistropic_uv)):
                pass
                self._io.write_f4le(self.f_anistropic_uv[i])

            self._io.write_f4le(self.f_primary_expo)
            self._io.write_f4le(self.f_secondary_expo)
            for i in range(len(self.f_primary_color)):
                pass
                self._io.write_f4le(self.f_primary_color[i])

            self._io.write_f4le(self.padding_4)
            for i in range(len(self.f_secondary_color)):
                pass
                self._io.write_f4le(self.f_secondary_color[i])

            self._io.write_f4le(self.padding_5)
            for i in range(len(self.xyzw_sepalate)):
                pass
                self._io.write_f4le(self.xyzw_sepalate[i])



        def _check(self):
            pass
            if (len(self.f_albedo_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color", len(self.f_albedo_color), 3)
            for i in range(len(self.f_albedo_color)):
                pass

            if (len(self.f_albedo_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend_color", len(self.f_albedo_blend_color), 4)
            for i in range(len(self.f_albedo_blend_color)):
                pass

            if (len(self.padding_2) != 2):
                raise kaitaistruct.ConsistencyError(u"padding_2", len(self.padding_2), 2)
            for i in range(len(self.padding_2)):
                pass

            if (len(self.f_light_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_light_map_color", len(self.f_light_map_color), 3)
            for i in range(len(self.f_light_map_color)):
                pass

            if (len(self.f_thin_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_thin_map_color", len(self.f_thin_map_color), 3)
            for i in range(len(self.f_thin_map_color)):
                pass

            if (len(self.f_indirect_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_offset", len(self.f_indirect_offset), 2)
            for i in range(len(self.f_indirect_offset)):
                pass

            if (len(self.f_indirect_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_scale", len(self.f_indirect_scale), 2)
            for i in range(len(self.f_indirect_scale)):
                pass

            if (len(self.f_fresnel_schlick_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_fresnel_schlick_rgb", len(self.f_fresnel_schlick_rgb), 3)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            if (len(self.f_specular_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color", len(self.f_specular_color), 3)
            for i in range(len(self.f_specular_color)):
                pass

            if (len(self.f_emission_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_emission_color", len(self.f_emission_color), 3)
            for i in range(len(self.f_emission_color)):
                pass

            if (len(self.f_roughness_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_roughness_rgb", len(self.f_roughness_rgb), 3)
            for i in range(len(self.f_roughness_rgb)):
                pass

            if (len(self.f_anisotoropic_direction) != 3):
                raise kaitaistruct.ConsistencyError(u"f_anisotoropic_direction", len(self.f_anisotoropic_direction), 3)
            for i in range(len(self.f_anisotoropic_direction)):
                pass

            if (len(self.f_anistropic_uv) != 2):
                raise kaitaistruct.ConsistencyError(u"f_anistropic_uv", len(self.f_anistropic_uv), 2)
            for i in range(len(self.f_anistropic_uv)):
                pass

            if (len(self.f_primary_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_primary_color", len(self.f_primary_color), 3)
            for i in range(len(self.f_primary_color)):
                pass

            if (len(self.f_secondary_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_secondary_color", len(self.f_secondary_color), 3)
            for i in range(len(self.f_secondary_color)):
                pass

            if (len(self.xyzw_sepalate) != 16):
                raise kaitaistruct.ConsistencyError(u"xyzw_sepalate", len(self.xyzw_sepalate), 16)
            for i in range(len(self.xyzw_sepalate)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 320
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbBurnCommon1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_b_blend_map_color = []
            for i in range(3):
                self.f_b_blend_map_color.append(self._io.read_f4le())

            self.f_b_alpha_clip_threshold = self._io.read_f4le()
            self.f_b_blend_alpha_threshold = self._io.read_f4le()
            self.f_b_blend_alpha_band = self._io.read_f4le()
            self.f_b_specular_blend_rate = self._io.read_f4le()
            self.f_b_albedo_blend_rate = self._io.read_f4le()
            self.f_b_albedo_blend_rate2 = self._io.read_f4le()
            self.padding = []
            for i in range(3):
                self.padding.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_b_blend_map_color)):
                pass

            for i in range(len(self.padding)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbBurnCommon1, self)._write__seq(io)
            for i in range(len(self.f_b_blend_map_color)):
                pass
                self._io.write_f4le(self.f_b_blend_map_color[i])

            self._io.write_f4le(self.f_b_alpha_clip_threshold)
            self._io.write_f4le(self.f_b_blend_alpha_threshold)
            self._io.write_f4le(self.f_b_blend_alpha_band)
            self._io.write_f4le(self.f_b_specular_blend_rate)
            self._io.write_f4le(self.f_b_albedo_blend_rate)
            self._io.write_f4le(self.f_b_albedo_blend_rate2)
            for i in range(len(self.padding)):
                pass
                self._io.write_f4le(self.padding[i])



        def _check(self):
            pass
            if (len(self.f_b_blend_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_b_blend_map_color", len(self.f_b_blend_map_color), 3)
            for i in range(len(self.f_b_blend_map_color)):
                pass

            if (len(self.padding) != 3):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 3)
            for i in range(len(self.padding)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 48
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimOfs(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_anim_entries = False
            self.anim_entries__to_write = True

        def _read(self):
            self.ofs_block = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.anim_entries
            self.anim_entries._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.AnimOfs, self)._write__seq(io)
            self._should_write_anim_entries = self.anim_entries__to_write
            self._io.write_u4le(self.ofs_block)


        def _check(self):
            pass

        @property
        def anim_entries(self):
            if self._should_write_anim_entries:
                self._write_anim_entries()
            if hasattr(self, '_m_anim_entries'):
                return self._m_anim_entries

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_anim_data + self.ofs_block))
            self._m_anim_entries = Mrl.AnimEntry(self._io, self, self._root)
            self._m_anim_entries._read()
            self._io.seek(_pos)
            return getattr(self, '_m_anim_entries', None)

        @anim_entries.setter
        def anim_entries(self, v):
            self._m_anim_entries = v

        def _write_anim_entries(self):
            self._should_write_anim_entries = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_anim_data + self.ofs_block))
            self.anim_entries._write__seq(self._io)
            self._io.seek(_pos)


        def _check_anim_entries(self):
            pass
            if self.anim_entries._root != self._root:
                raise kaitaistruct.ConsistencyError(u"anim_entries", self.anim_entries._root, self._root)
            if self.anim_entries._parent != self:
                raise kaitaistruct.ConsistencyError(u"anim_entries", self.anim_entries._parent, self)


    class AnimSubEntry0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                _t_values = Mrl.AnimType0(self._io, self, self._root)
                _t_values._read()
                self.values.append(_t_values)



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass
                self.values[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry0, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self.values[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.header) != 4):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 4)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != self._parent.info.num_entry):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), self._parent.info.num_entry)
            for i in range(len(self.values)):
                pass
                if self.values[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._root, self._root)
                if self.values[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._parent, self)



    class CbDdMaterialParamInnerCorrect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbDdMaterialParamInnerCorrect, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbDdMaterialParamInnerCorrect1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbDdMaterialParamInnerCorrect1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbBurnEmission(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbBurnEmission, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbBurnEmission1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbBurnEmission1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbUvRotationOffset1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_uv_rotation_center = []
            for i in range(2):
                self.f_uv_rotation_center.append(self._io.read_f4le())

            self.f_uv_rotation_angle = self._io.read_f4le()
            self.padding = self._io.read_f4le()
            self.f_uv_rotation_offset = []
            for i in range(2):
                self.f_uv_rotation_offset.append(self._io.read_f4le())

            self.f_uv_rotation_scale = []
            for i in range(2):
                self.f_uv_rotation_scale.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_uv_rotation_center)):
                pass

            for i in range(len(self.f_uv_rotation_offset)):
                pass

            for i in range(len(self.f_uv_rotation_scale)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbUvRotationOffset1, self)._write__seq(io)
            for i in range(len(self.f_uv_rotation_center)):
                pass
                self._io.write_f4le(self.f_uv_rotation_center[i])

            self._io.write_f4le(self.f_uv_rotation_angle)
            self._io.write_f4le(self.padding)
            for i in range(len(self.f_uv_rotation_offset)):
                pass
                self._io.write_f4le(self.f_uv_rotation_offset[i])

            for i in range(len(self.f_uv_rotation_scale)):
                pass
                self._io.write_f4le(self.f_uv_rotation_scale[i])



        def _check(self):
            pass
            if (len(self.f_uv_rotation_center) != 2):
                raise kaitaistruct.ConsistencyError(u"f_uv_rotation_center", len(self.f_uv_rotation_center), 2)
            for i in range(len(self.f_uv_rotation_center)):
                pass

            if (len(self.f_uv_rotation_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_uv_rotation_offset", len(self.f_uv_rotation_offset), 2)
            for i in range(len(self.f_uv_rotation_offset)):
                pass

            if (len(self.f_uv_rotation_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_uv_rotation_scale", len(self.f_uv_rotation_scale), 2)
            for i in range(len(self.f_uv_rotation_scale)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbUvRotationOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbUvRotationOffset, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbUvRotationOffset1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbUvRotationOffset1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbVertexDisplacement1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_vtx_disp_start = self._io.read_f4le()
            self.f_vtx_disp_scale = self._io.read_f4le()
            self.f_vtx_disp_inv_area = self._io.read_f4le()
            self.f_vtx_disp_rcn = self._io.read_f4le()
            self.f_vtx_disp_tilt_u = self._io.read_f4le()
            self.f_vtx_disp_tilt_v = self._io.read_f4le()
            self.filler = []
            for i in range(2):
                self.filler.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.filler)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbVertexDisplacement1, self)._write__seq(io)
            self._io.write_f4le(self.f_vtx_disp_start)
            self._io.write_f4le(self.f_vtx_disp_scale)
            self._io.write_f4le(self.f_vtx_disp_inv_area)
            self._io.write_f4le(self.f_vtx_disp_rcn)
            self._io.write_f4le(self.f_vtx_disp_tilt_u)
            self._io.write_f4le(self.f_vtx_disp_tilt_v)
            for i in range(len(self.filler)):
                pass
                self._io.write_f4le(self.filler[i])



        def _check(self):
            pass
            if (len(self.filler) != 2):
                raise kaitaistruct.ConsistencyError(u"filler", len(self.filler), 2)
            for i in range(len(self.filler)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimSubEntry7(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(36):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((24 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry7, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self._io.write_u1(self.values[i])



        def _check(self):
            pass
            if (len(self.header) != 36):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 36)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != (24 * (self._parent.info.num_entry - 1))):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), (24 * (self._parent.info.num_entry - 1)))
            for i in range(len(self.values)):
                pass



    class ShdHash(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.shader_hash = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.ShdHash, self)._write__seq(io)
            self._io.write_u4le(self.shader_hash)


        def _check(self):
            pass


    class AnimType0(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.AnimType0, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            self._io.write_f4le(self.unk_01)


        def _check(self):
            pass


    class CbBurnCommon(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbBurnCommon, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbBurnCommon1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbBurnCommon1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class TextureSlot(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type_hash = KaitaiStream.resolve_enum(Mrl.TextureType, self._io.read_u4le())
            self.unk_02 = self._io.read_u4le()
            self.unk_03 = self._io.read_u4le()
            self.texture_path = (self._io.read_bytes_term(0, False, True, True)).decode("ASCII")
            self.filler = []
            for i in range(((64 - len(self.texture_path)) - 1)):
                self.filler.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.filler)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.TextureSlot, self)._write__seq(io)
            self._io.write_u4le(int(self.type_hash))
            self._io.write_u4le(self.unk_02)
            self._io.write_u4le(self.unk_03)
            self._io.write_bytes((self.texture_path).encode(u"ASCII"))
            self._io.write_u1(0)
            for i in range(len(self.filler)):
                pass
                self._io.write_u1(self.filler[i])



        def _check(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.texture_path).encode(u"ASCII"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"texture_path", KaitaiStream.byte_array_index_of((self.texture_path).encode(u"ASCII"), 0), -1)
            if (len(self.filler) != ((64 - len(self.texture_path)) - 1)):
                raise kaitaistruct.ConsistencyError(u"filler", len(self.filler), ((64 - len(self.texture_path)) - 1))
            for i in range(len(self.filler)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 76
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class BlockOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_body = False
            self.body__to_write = True

        def _read(self):
            self.ofc_block = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.body
            self.body._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.BlockOffset, self)._write__seq(io)
            self._should_write_body = self.body__to_write
            self._io.write_u4le(self.ofc_block)


        def _check(self):
            pass

        @property
        def body(self):
            if self._should_write_body:
                self._write_body()
            if hasattr(self, '_m_body'):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek((self._parent._parent._parent.ofs_base + self.ofc_block))
            self._m_body = Mrl.AnimSubEntry(self._io, self, self._root)
            self._m_body._read()
            self._io.seek(_pos)
            return getattr(self, '_m_body', None)

        @body.setter
        def body(self, v):
            self._m_body = v

        def _write_body(self):
            self._should_write_body = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent._parent.ofs_base + self.ofc_block))
            self.body._write__seq(self._io)
            self._io.seek(_pos)


        def _check_body(self):
            pass
            if self.body._root != self._root:
                raise kaitaistruct.ConsistencyError(u"body", self.body._root, self._root)
            if self.body._parent != self:
                raise kaitaistruct.ConsistencyError(u"body", self.body._parent, self)


    class CbGlobals3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.padding_1 = self._io.read_f4le()
            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = self._io.read_f4le()
            self.padding_2 = []
            for i in range(2):
                self.padding_2.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(3):
                self.f_light_map_color.append(self._io.read_f4le())

            self.padding_3 = self._io.read_f4le()
            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(3):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.padding_4 = []
            for i in range(2):
                self.padding_4.append(self._io.read_f4le())

            self.f_primary_color = []
            for i in range(3):
                self.f_primary_color.append(self._io.read_f4le())

            self.padding_5 = self._io.read_f4le()
            self.f_secondary_color = []
            for i in range(3):
                self.f_secondary_color.append(self._io.read_f4le())

            self.padding_6 = self._io.read_f4le()
            self.f_albedo_color_2 = []
            for i in range(3):
                self.f_albedo_color_2.append(self._io.read_f4le())

            self.padding_7 = self._io.read_f4le()
            self.f_specular_color_2 = []
            for i in range(3):
                self.f_specular_color_2.append(self._io.read_f4le())

            self.f_fresnel_schlick_2 = self._io.read_f4le()
            self.f_shininess_2 = self._io.read_f4le()
            self.padding_8 = []
            for i in range(3):
                self.padding_8.append(self._io.read_f4le())

            self.f_transparency_clip_threshold = []
            for i in range(4):
                self.f_transparency_clip_threshold.append(self._io.read_f4le())

            self.f_blend_uv = self._io.read_f4le()
            self.padding_9 = []
            for i in range(3):
                self.padding_9.append(self._io.read_f4le())

            self.f_albedo_blend2_color = []
            for i in range(4):
                self.f_albedo_blend2_color.append(self._io.read_f4le())

            self.f_detail_normalu_vscale = []
            for i in range(2):
                self.f_detail_normalu_vscale.append(self._io.read_f4le())

            self.padding_10 = []
            for i in range(2):
                self.padding_10.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_albedo_color)):
                pass

            for i in range(len(self.f_albedo_blend_color)):
                pass

            for i in range(len(self.padding_2)):
                pass

            for i in range(len(self.f_light_map_color)):
                pass

            for i in range(len(self.f_thin_map_color)):
                pass

            for i in range(len(self.f_indirect_offset)):
                pass

            for i in range(len(self.f_indirect_scale)):
                pass

            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            for i in range(len(self.f_specular_color)):
                pass

            for i in range(len(self.f_emission_color)):
                pass

            for i in range(len(self.padding_4)):
                pass

            for i in range(len(self.f_primary_color)):
                pass

            for i in range(len(self.f_secondary_color)):
                pass

            for i in range(len(self.f_albedo_color_2)):
                pass

            for i in range(len(self.f_specular_color_2)):
                pass

            for i in range(len(self.padding_8)):
                pass

            for i in range(len(self.f_transparency_clip_threshold)):
                pass

            for i in range(len(self.padding_9)):
                pass

            for i in range(len(self.f_albedo_blend2_color)):
                pass

            for i in range(len(self.f_detail_normalu_vscale)):
                pass

            for i in range(len(self.padding_10)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbGlobals3, self)._write__seq(io)
            for i in range(len(self.f_albedo_color)):
                pass
                self._io.write_f4le(self.f_albedo_color[i])

            self._io.write_f4le(self.padding_1)
            for i in range(len(self.f_albedo_blend_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend_color[i])

            self._io.write_f4le(self.f_detail_normal_power)
            self._io.write_f4le(self.f_detail_normal_uv_scale)
            self._io.write_f4le(self.f_detail_normal2_power)
            self._io.write_f4le(self.f_detail_normal2_uv_scale)
            self._io.write_f4le(self.f_primary_shift)
            self._io.write_f4le(self.f_secondary_shift)
            self._io.write_f4le(self.f_parallax_factor)
            self._io.write_f4le(self.f_parallax_self_occlusion)
            self._io.write_f4le(self.f_parallax_min_sample)
            self._io.write_f4le(self.f_parallax_max_sample)
            for i in range(len(self.padding_2)):
                pass
                self._io.write_f4le(self.padding_2[i])

            for i in range(len(self.f_light_map_color)):
                pass
                self._io.write_f4le(self.f_light_map_color[i])

            self._io.write_f4le(self.padding_3)
            for i in range(len(self.f_thin_map_color)):
                pass
                self._io.write_f4le(self.f_thin_map_color[i])

            self._io.write_f4le(self.f_thin_scattering)
            for i in range(len(self.f_indirect_offset)):
                pass
                self._io.write_f4le(self.f_indirect_offset[i])

            for i in range(len(self.f_indirect_scale)):
                pass
                self._io.write_f4le(self.f_indirect_scale[i])

            self._io.write_f4le(self.f_fresnel_schlick)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass
                self._io.write_f4le(self.f_fresnel_schlick_rgb[i])

            for i in range(len(self.f_specular_color)):
                pass
                self._io.write_f4le(self.f_specular_color[i])

            self._io.write_f4le(self.f_shininess)
            for i in range(len(self.f_emission_color)):
                pass
                self._io.write_f4le(self.f_emission_color[i])

            self._io.write_f4le(self.f_alpha_clip_threshold)
            self._io.write_f4le(self.f_primary_expo)
            self._io.write_f4le(self.f_secondary_expo)
            for i in range(len(self.padding_4)):
                pass
                self._io.write_f4le(self.padding_4[i])

            for i in range(len(self.f_primary_color)):
                pass
                self._io.write_f4le(self.f_primary_color[i])

            self._io.write_f4le(self.padding_5)
            for i in range(len(self.f_secondary_color)):
                pass
                self._io.write_f4le(self.f_secondary_color[i])

            self._io.write_f4le(self.padding_6)
            for i in range(len(self.f_albedo_color_2)):
                pass
                self._io.write_f4le(self.f_albedo_color_2[i])

            self._io.write_f4le(self.padding_7)
            for i in range(len(self.f_specular_color_2)):
                pass
                self._io.write_f4le(self.f_specular_color_2[i])

            self._io.write_f4le(self.f_fresnel_schlick_2)
            self._io.write_f4le(self.f_shininess_2)
            for i in range(len(self.padding_8)):
                pass
                self._io.write_f4le(self.padding_8[i])

            for i in range(len(self.f_transparency_clip_threshold)):
                pass
                self._io.write_f4le(self.f_transparency_clip_threshold[i])

            self._io.write_f4le(self.f_blend_uv)
            for i in range(len(self.padding_9)):
                pass
                self._io.write_f4le(self.padding_9[i])

            for i in range(len(self.f_albedo_blend2_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend2_color[i])

            for i in range(len(self.f_detail_normalu_vscale)):
                pass
                self._io.write_f4le(self.f_detail_normalu_vscale[i])

            for i in range(len(self.padding_10)):
                pass
                self._io.write_f4le(self.padding_10[i])



        def _check(self):
            pass
            if (len(self.f_albedo_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color", len(self.f_albedo_color), 3)
            for i in range(len(self.f_albedo_color)):
                pass

            if (len(self.f_albedo_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend_color", len(self.f_albedo_blend_color), 4)
            for i in range(len(self.f_albedo_blend_color)):
                pass

            if (len(self.padding_2) != 2):
                raise kaitaistruct.ConsistencyError(u"padding_2", len(self.padding_2), 2)
            for i in range(len(self.padding_2)):
                pass

            if (len(self.f_light_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_light_map_color", len(self.f_light_map_color), 3)
            for i in range(len(self.f_light_map_color)):
                pass

            if (len(self.f_thin_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_thin_map_color", len(self.f_thin_map_color), 3)
            for i in range(len(self.f_thin_map_color)):
                pass

            if (len(self.f_indirect_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_offset", len(self.f_indirect_offset), 2)
            for i in range(len(self.f_indirect_offset)):
                pass

            if (len(self.f_indirect_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_scale", len(self.f_indirect_scale), 2)
            for i in range(len(self.f_indirect_scale)):
                pass

            if (len(self.f_fresnel_schlick_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_fresnel_schlick_rgb", len(self.f_fresnel_schlick_rgb), 3)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            if (len(self.f_specular_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color", len(self.f_specular_color), 3)
            for i in range(len(self.f_specular_color)):
                pass

            if (len(self.f_emission_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_emission_color", len(self.f_emission_color), 3)
            for i in range(len(self.f_emission_color)):
                pass

            if (len(self.padding_4) != 2):
                raise kaitaistruct.ConsistencyError(u"padding_4", len(self.padding_4), 2)
            for i in range(len(self.padding_4)):
                pass

            if (len(self.f_primary_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_primary_color", len(self.f_primary_color), 3)
            for i in range(len(self.f_primary_color)):
                pass

            if (len(self.f_secondary_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_secondary_color", len(self.f_secondary_color), 3)
            for i in range(len(self.f_secondary_color)):
                pass

            if (len(self.f_albedo_color_2) != 3):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color_2", len(self.f_albedo_color_2), 3)
            for i in range(len(self.f_albedo_color_2)):
                pass

            if (len(self.f_specular_color_2) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color_2", len(self.f_specular_color_2), 3)
            for i in range(len(self.f_specular_color_2)):
                pass

            if (len(self.padding_8) != 3):
                raise kaitaistruct.ConsistencyError(u"padding_8", len(self.padding_8), 3)
            for i in range(len(self.padding_8)):
                pass

            if (len(self.f_transparency_clip_threshold) != 4):
                raise kaitaistruct.ConsistencyError(u"f_transparency_clip_threshold", len(self.f_transparency_clip_threshold), 4)
            for i in range(len(self.f_transparency_clip_threshold)):
                pass

            if (len(self.padding_9) != 3):
                raise kaitaistruct.ConsistencyError(u"padding_9", len(self.padding_9), 3)
            for i in range(len(self.padding_9)):
                pass

            if (len(self.f_albedo_blend2_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend2_color", len(self.f_albedo_blend2_color), 4)
            for i in range(len(self.f_albedo_blend2_color)):
                pass

            if (len(self.f_detail_normalu_vscale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_detail_normalu_vscale", len(self.f_detail_normalu_vscale), 2)
            for i in range(len(self.f_detail_normalu_vscale)):
                pass

            if (len(self.padding_10) != 2):
                raise kaitaistruct.ConsistencyError(u"padding_10", len(self.padding_10), 2)
            for i in range(len(self.padding_10)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 336
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CmdOfsBuffer(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ofs_float_buff = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.CmdOfsBuffer, self)._write__seq(io)
            self._io.write_u4le(self.ofs_float_buff)


        def _check(self):
            pass


    class CbDistortion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_distortion_factor = self._io.read_f4le()
            self.f_distortion_blend = self._io.read_f4le()
            self.filler = []
            for i in range(2):
                self.filler.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.filler)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbDistortion, self)._write__seq(io)
            self._io.write_f4le(self.f_distortion_factor)
            self._io.write_f4le(self.f_distortion_blend)
            for i in range(len(self.filler)):
                pass
                self._io.write_f4le(self.filler[i])



        def _check(self):
            pass
            if (len(self.filler) != 2):
                raise kaitaistruct.ConsistencyError(u"filler", len(self.filler), 2)
            for i in range(len(self.filler)):
                pass



    class CbAppReflectShadowLight(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbAppReflectShadowLight, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbAppReflectShadowLight1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbAppReflectShadowLight1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbColorMask1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_color_mask_threshold = []
            for i in range(4):
                self.f_color_mask_threshold.append(self._io.read_f4le())

            self.f_color_mask_offset = []
            for i in range(4):
                self.f_color_mask_offset.append(self._io.read_f4le())

            self.f_clip_threshold = []
            for i in range(4):
                self.f_clip_threshold.append(self._io.read_f4le())

            self.f_color_mask_color = []
            for i in range(4):
                self.f_color_mask_color.append(self._io.read_f4le())

            self.f_color_mask2_threshold = []
            for i in range(4):
                self.f_color_mask2_threshold.append(self._io.read_f4le())

            self.f_color_mask2_color = []
            for i in range(4):
                self.f_color_mask2_color.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_color_mask_threshold)):
                pass

            for i in range(len(self.f_color_mask_offset)):
                pass

            for i in range(len(self.f_clip_threshold)):
                pass

            for i in range(len(self.f_color_mask_color)):
                pass

            for i in range(len(self.f_color_mask2_threshold)):
                pass

            for i in range(len(self.f_color_mask2_color)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbColorMask1, self)._write__seq(io)
            for i in range(len(self.f_color_mask_threshold)):
                pass
                self._io.write_f4le(self.f_color_mask_threshold[i])

            for i in range(len(self.f_color_mask_offset)):
                pass
                self._io.write_f4le(self.f_color_mask_offset[i])

            for i in range(len(self.f_clip_threshold)):
                pass
                self._io.write_f4le(self.f_clip_threshold[i])

            for i in range(len(self.f_color_mask_color)):
                pass
                self._io.write_f4le(self.f_color_mask_color[i])

            for i in range(len(self.f_color_mask2_threshold)):
                pass
                self._io.write_f4le(self.f_color_mask2_threshold[i])

            for i in range(len(self.f_color_mask2_color)):
                pass
                self._io.write_f4le(self.f_color_mask2_color[i])



        def _check(self):
            pass
            if (len(self.f_color_mask_threshold) != 4):
                raise kaitaistruct.ConsistencyError(u"f_color_mask_threshold", len(self.f_color_mask_threshold), 4)
            for i in range(len(self.f_color_mask_threshold)):
                pass

            if (len(self.f_color_mask_offset) != 4):
                raise kaitaistruct.ConsistencyError(u"f_color_mask_offset", len(self.f_color_mask_offset), 4)
            for i in range(len(self.f_color_mask_offset)):
                pass

            if (len(self.f_clip_threshold) != 4):
                raise kaitaistruct.ConsistencyError(u"f_clip_threshold", len(self.f_clip_threshold), 4)
            for i in range(len(self.f_clip_threshold)):
                pass

            if (len(self.f_color_mask_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_color_mask_color", len(self.f_color_mask_color), 4)
            for i in range(len(self.f_color_mask_color)):
                pass

            if (len(self.f_color_mask2_threshold) != 4):
                raise kaitaistruct.ConsistencyError(u"f_color_mask2_threshold", len(self.f_color_mask2_threshold), 4)
            for i in range(len(self.f_color_mask2_threshold)):
                pass

            if (len(self.f_color_mask2_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_color_mask2_color", len(self.f_color_mask2_color), 4)
            for i in range(len(self.f_color_mask2_color)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 96
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimType6(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = []
            for i in range(2):
                self.unk_00.append(self._io.read_u4le())

            self.unk_01 = []
            for i in range(4):
                self.unk_01.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_00)):
                pass

            for i in range(len(self.unk_01)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimType6, self)._write__seq(io)
            for i in range(len(self.unk_00)):
                pass
                self._io.write_u4le(self.unk_00[i])

            for i in range(len(self.unk_01)):
                pass
                self._io.write_f4le(self.unk_01[i])



        def _check(self):
            pass
            if (len(self.unk_00) != 2):
                raise kaitaistruct.ConsistencyError(u"unk_00", len(self.unk_00), 2)
            for i in range(len(self.unk_00)):
                pass

            if (len(self.unk_01) != 4):
                raise kaitaistruct.ConsistencyError(u"unk_01", len(self.unk_01), 4)
            for i in range(len(self.unk_01)):
                pass



    class AnimDataInfo(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.type = self._io.read_bits_int_le(4)
            self.unk_00 = self._io.read_bits_int_le(4)
            self.num_entry = self._io.read_bits_int_le(24)


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.AnimDataInfo, self)._write__seq(io)
            self._io.write_bits_int_le(4, self.type)
            self._io.write_bits_int_le(4, self.unk_00)
            self._io.write_bits_int_le(24, self.num_entry)


        def _check(self):
            pass


    class AnimSubEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.shader_hash = self._io.read_u4le()
            self.info = Mrl.AnimDataInfo(self._io, self, self._root)
            self.info._read()
            _on = self.info.type
            if _on == 0:
                pass
                self.entry = Mrl.AnimSubEntry0(self._io, self, self._root)
                self.entry._read()
            elif _on == 4:
                pass
                self.entry = Mrl.AnimSubEntry4(self._io, self, self._root)
                self.entry._read()
            elif _on == 6:
                pass
                self.entry = Mrl.AnimSubEntry6(self._io, self, self._root)
                self.entry._read()
            elif _on == 7:
                pass
                self.entry = Mrl.AnimSubEntry7(self._io, self, self._root)
                self.entry._read()
            elif _on == 1:
                pass
                self.entry = Mrl.AnimSubEntry1(self._io, self, self._root)
                self.entry._read()
            elif _on == 3:
                pass
                self.entry = Mrl.AnimSubEntry3(self._io, self, self._root)
                self.entry._read()
            elif _on == 5:
                pass
                self.entry = Mrl.AnimSubEntry5(self._io, self, self._root)
                self.entry._read()
            elif _on == 2:
                pass
                self.entry = Mrl.AnimSubEntry2(self._io, self, self._root)
                self.entry._read()


        def _fetch_instances(self):
            pass
            self.info._fetch_instances()
            _on = self.info.type
            if _on == 0:
                pass
                self.entry._fetch_instances()
            elif _on == 4:
                pass
                self.entry._fetch_instances()
            elif _on == 6:
                pass
                self.entry._fetch_instances()
            elif _on == 7:
                pass
                self.entry._fetch_instances()
            elif _on == 1:
                pass
                self.entry._fetch_instances()
            elif _on == 3:
                pass
                self.entry._fetch_instances()
            elif _on == 5:
                pass
                self.entry._fetch_instances()
            elif _on == 2:
                pass
                self.entry._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry, self)._write__seq(io)
            self._io.write_u4le(self.shader_hash)
            self.info._write__seq(self._io)
            _on = self.info.type
            if _on == 0:
                pass
                self.entry._write__seq(self._io)
            elif _on == 4:
                pass
                self.entry._write__seq(self._io)
            elif _on == 6:
                pass
                self.entry._write__seq(self._io)
            elif _on == 7:
                pass
                self.entry._write__seq(self._io)
            elif _on == 1:
                pass
                self.entry._write__seq(self._io)
            elif _on == 3:
                pass
                self.entry._write__seq(self._io)
            elif _on == 5:
                pass
                self.entry._write__seq(self._io)
            elif _on == 2:
                pass
                self.entry._write__seq(self._io)


        def _check(self):
            pass
            if self.info._root != self._root:
                raise kaitaistruct.ConsistencyError(u"info", self.info._root, self._root)
            if self.info._parent != self:
                raise kaitaistruct.ConsistencyError(u"info", self.info._parent, self)
            _on = self.info.type
            if _on == 0:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 4:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 6:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 7:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 1:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 3:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 5:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)
            elif _on == 2:
                pass
                if self.entry._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._root, self._root)
                if self.entry._parent != self:
                    raise kaitaistruct.ConsistencyError(u"entry", self.entry._parent, self)


    class AnimSubEntry4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                _t_values = Mrl.AnimType4(self._io, self, self._root)
                _t_values._read()
                self.values.append(_t_values)

            self.hash = []
            for i in range(self._parent.info.num_entry):
                self.hash.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass
                self.values[i]._fetch_instances()

            for i in range(len(self.hash)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry4, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self.values[i]._write__seq(self._io)

            for i in range(len(self.hash)):
                pass
                self._io.write_u4le(self.hash[i])



        def _check(self):
            pass
            if (len(self.header) != 4):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 4)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != self._parent.info.num_entry):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), self._parent.info.num_entry)
            for i in range(len(self.values)):
                pass
                if self.values[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._root, self._root)
                if self.values[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._parent, self)

            if (len(self.hash) != self._parent.info.num_entry):
                raise kaitaistruct.ConsistencyError(u"hash", len(self.hash), self._parent.info.num_entry)
            for i in range(len(self.hash)):
                pass



    class CbSpecularBlend(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbSpecularBlend, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbSpecularBlend1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbSpecularBlend1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbDdMaterialParamInnerCorrect1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_dd_material_inner_correct_offset = self._io.read_f4le()
            self.padding = []
            for i in range(3):
                self.padding.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.padding)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbDdMaterialParamInnerCorrect1, self)._write__seq(io)
            self._io.write_f4le(self.f_dd_material_inner_correct_offset)
            for i in range(len(self.padding)):
                pass
                self._io.write_f4le(self.padding[i])



        def _check(self):
            pass
            if (len(self.padding) != 3):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 3)
            for i in range(len(self.padding)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbDdMaterialParam(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbDdMaterialParam, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbDdMaterialParam1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbDdMaterialParam1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class CbGlobals2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_alpha_clip_threshold = self._io.read_f4le()
            self.f_albedo_color = []
            for i in range(3):
                self.f_albedo_color.append(self._io.read_f4le())

            self.f_albedo_blend_color = []
            for i in range(4):
                self.f_albedo_blend_color.append(self._io.read_f4le())

            self.f_detail_normal_power = self._io.read_f4le()
            self.f_detail_normal_uv_scale = self._io.read_f4le()
            self.f_detail_normal2_power = self._io.read_f4le()
            self.f_detail_normal2_uv_scale = self._io.read_f4le()
            self.f_primary_shift = self._io.read_f4le()
            self.f_secondary_shift = self._io.read_f4le()
            self.f_parallax_factor = self._io.read_f4le()
            self.f_parallax_self_occlusion = self._io.read_f4le()
            self.f_parallax_min_sample = self._io.read_f4le()
            self.f_parallax_max_sample = []
            for i in range(3):
                self.f_parallax_max_sample.append(self._io.read_f4le())

            self.f_light_map_color = []
            for i in range(4):
                self.f_light_map_color.append(self._io.read_f4le())

            self.f_thin_map_color = []
            for i in range(3):
                self.f_thin_map_color.append(self._io.read_f4le())

            self.f_thin_scattering = self._io.read_f4le()
            self.f_screen_uv_scale = []
            for i in range(2):
                self.f_screen_uv_scale.append(self._io.read_f4le())

            self.f_screen_uv_offset = []
            for i in range(2):
                self.f_screen_uv_offset.append(self._io.read_f4le())

            self.f_indirect_offset = []
            for i in range(2):
                self.f_indirect_offset.append(self._io.read_f4le())

            self.f_indirect_scale = []
            for i in range(2):
                self.f_indirect_scale.append(self._io.read_f4le())

            self.f_fresnel_schlick = self._io.read_f4le()
            self.f_fresnel_schlick_rgb = []
            for i in range(3):
                self.f_fresnel_schlick_rgb.append(self._io.read_f4le())

            self.f_specular_color = []
            for i in range(3):
                self.f_specular_color.append(self._io.read_f4le())

            self.f_shininess = self._io.read_f4le()
            self.f_emission_color = []
            for i in range(3):
                self.f_emission_color.append(self._io.read_f4le())

            self.f_emission_threshold = self._io.read_f4le()
            self.f_constant_color = []
            for i in range(4):
                self.f_constant_color.append(self._io.read_f4le())

            self.f_roughness = self._io.read_f4le()
            self.f_roughness_rgb = []
            for i in range(3):
                self.f_roughness_rgb.append(self._io.read_f4le())

            self.f_anisotoropic_direction = []
            for i in range(3):
                self.f_anisotoropic_direction.append(self._io.read_f4le())

            self.f_smoothness = self._io.read_f4le()
            self.f_anistropic_uv = []
            for i in range(2):
                self.f_anistropic_uv.append(self._io.read_f4le())

            self.f_primary_expo = self._io.read_f4le()
            self.f_secondary_expo = self._io.read_f4le()
            self.f_primary_color = []
            for i in range(4):
                self.f_primary_color.append(self._io.read_f4le())

            self.f_secondary_color = []
            for i in range(4):
                self.f_secondary_color.append(self._io.read_f4le())

            self.f_albedo_color2 = []
            for i in range(4):
                self.f_albedo_color2.append(self._io.read_f4le())

            self.f_specular_color2 = []
            for i in range(3):
                self.f_specular_color2.append(self._io.read_f4le())

            self.f_fresnel_schlick2 = self._io.read_f4le()
            self.f_shininess2 = []
            for i in range(4):
                self.f_shininess2.append(self._io.read_f4le())

            self.f_transparency_clip_threshold = []
            for i in range(4):
                self.f_transparency_clip_threshold.append(self._io.read_f4le())

            self.f_blend_uv = self._io.read_f4le()
            self.f_normal_power = []
            for i in range(3):
                self.f_normal_power.append(self._io.read_f4le())

            self.f_albedo_blend2_color = []
            for i in range(4):
                self.f_albedo_blend2_color.append(self._io.read_f4le())

            self.f_detail_normal_u_v_scale = []
            for i in range(2):
                self.f_detail_normal_u_v_scale.append(self._io.read_f4le())

            self.f_fresnel_legacy = []
            for i in range(2):
                self.f_fresnel_legacy.append(self._io.read_f4le())

            self.f_normal_mask_pow0 = []
            for i in range(4):
                self.f_normal_mask_pow0.append(self._io.read_f4le())

            self.f_normal_mask_pow1 = []
            for i in range(4):
                self.f_normal_mask_pow1.append(self._io.read_f4le())

            self.f_normal_mask_pow2 = []
            for i in range(4):
                self.f_normal_mask_pow2.append(self._io.read_f4le())

            self.f_texture_blend_rate = []
            for i in range(4):
                self.f_texture_blend_rate.append(self._io.read_f4le())

            self.f_texture_blend_color = []
            for i in range(4):
                self.f_texture_blend_color.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_albedo_color)):
                pass

            for i in range(len(self.f_albedo_blend_color)):
                pass

            for i in range(len(self.f_parallax_max_sample)):
                pass

            for i in range(len(self.f_light_map_color)):
                pass

            for i in range(len(self.f_thin_map_color)):
                pass

            for i in range(len(self.f_screen_uv_scale)):
                pass

            for i in range(len(self.f_screen_uv_offset)):
                pass

            for i in range(len(self.f_indirect_offset)):
                pass

            for i in range(len(self.f_indirect_scale)):
                pass

            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            for i in range(len(self.f_specular_color)):
                pass

            for i in range(len(self.f_emission_color)):
                pass

            for i in range(len(self.f_constant_color)):
                pass

            for i in range(len(self.f_roughness_rgb)):
                pass

            for i in range(len(self.f_anisotoropic_direction)):
                pass

            for i in range(len(self.f_anistropic_uv)):
                pass

            for i in range(len(self.f_primary_color)):
                pass

            for i in range(len(self.f_secondary_color)):
                pass

            for i in range(len(self.f_albedo_color2)):
                pass

            for i in range(len(self.f_specular_color2)):
                pass

            for i in range(len(self.f_shininess2)):
                pass

            for i in range(len(self.f_transparency_clip_threshold)):
                pass

            for i in range(len(self.f_normal_power)):
                pass

            for i in range(len(self.f_albedo_blend2_color)):
                pass

            for i in range(len(self.f_detail_normal_u_v_scale)):
                pass

            for i in range(len(self.f_fresnel_legacy)):
                pass

            for i in range(len(self.f_normal_mask_pow0)):
                pass

            for i in range(len(self.f_normal_mask_pow1)):
                pass

            for i in range(len(self.f_normal_mask_pow2)):
                pass

            for i in range(len(self.f_texture_blend_rate)):
                pass

            for i in range(len(self.f_texture_blend_color)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbGlobals2, self)._write__seq(io)
            self._io.write_f4le(self.f_alpha_clip_threshold)
            for i in range(len(self.f_albedo_color)):
                pass
                self._io.write_f4le(self.f_albedo_color[i])

            for i in range(len(self.f_albedo_blend_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend_color[i])

            self._io.write_f4le(self.f_detail_normal_power)
            self._io.write_f4le(self.f_detail_normal_uv_scale)
            self._io.write_f4le(self.f_detail_normal2_power)
            self._io.write_f4le(self.f_detail_normal2_uv_scale)
            self._io.write_f4le(self.f_primary_shift)
            self._io.write_f4le(self.f_secondary_shift)
            self._io.write_f4le(self.f_parallax_factor)
            self._io.write_f4le(self.f_parallax_self_occlusion)
            self._io.write_f4le(self.f_parallax_min_sample)
            for i in range(len(self.f_parallax_max_sample)):
                pass
                self._io.write_f4le(self.f_parallax_max_sample[i])

            for i in range(len(self.f_light_map_color)):
                pass
                self._io.write_f4le(self.f_light_map_color[i])

            for i in range(len(self.f_thin_map_color)):
                pass
                self._io.write_f4le(self.f_thin_map_color[i])

            self._io.write_f4le(self.f_thin_scattering)
            for i in range(len(self.f_screen_uv_scale)):
                pass
                self._io.write_f4le(self.f_screen_uv_scale[i])

            for i in range(len(self.f_screen_uv_offset)):
                pass
                self._io.write_f4le(self.f_screen_uv_offset[i])

            for i in range(len(self.f_indirect_offset)):
                pass
                self._io.write_f4le(self.f_indirect_offset[i])

            for i in range(len(self.f_indirect_scale)):
                pass
                self._io.write_f4le(self.f_indirect_scale[i])

            self._io.write_f4le(self.f_fresnel_schlick)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass
                self._io.write_f4le(self.f_fresnel_schlick_rgb[i])

            for i in range(len(self.f_specular_color)):
                pass
                self._io.write_f4le(self.f_specular_color[i])

            self._io.write_f4le(self.f_shininess)
            for i in range(len(self.f_emission_color)):
                pass
                self._io.write_f4le(self.f_emission_color[i])

            self._io.write_f4le(self.f_emission_threshold)
            for i in range(len(self.f_constant_color)):
                pass
                self._io.write_f4le(self.f_constant_color[i])

            self._io.write_f4le(self.f_roughness)
            for i in range(len(self.f_roughness_rgb)):
                pass
                self._io.write_f4le(self.f_roughness_rgb[i])

            for i in range(len(self.f_anisotoropic_direction)):
                pass
                self._io.write_f4le(self.f_anisotoropic_direction[i])

            self._io.write_f4le(self.f_smoothness)
            for i in range(len(self.f_anistropic_uv)):
                pass
                self._io.write_f4le(self.f_anistropic_uv[i])

            self._io.write_f4le(self.f_primary_expo)
            self._io.write_f4le(self.f_secondary_expo)
            for i in range(len(self.f_primary_color)):
                pass
                self._io.write_f4le(self.f_primary_color[i])

            for i in range(len(self.f_secondary_color)):
                pass
                self._io.write_f4le(self.f_secondary_color[i])

            for i in range(len(self.f_albedo_color2)):
                pass
                self._io.write_f4le(self.f_albedo_color2[i])

            for i in range(len(self.f_specular_color2)):
                pass
                self._io.write_f4le(self.f_specular_color2[i])

            self._io.write_f4le(self.f_fresnel_schlick2)
            for i in range(len(self.f_shininess2)):
                pass
                self._io.write_f4le(self.f_shininess2[i])

            for i in range(len(self.f_transparency_clip_threshold)):
                pass
                self._io.write_f4le(self.f_transparency_clip_threshold[i])

            self._io.write_f4le(self.f_blend_uv)
            for i in range(len(self.f_normal_power)):
                pass
                self._io.write_f4le(self.f_normal_power[i])

            for i in range(len(self.f_albedo_blend2_color)):
                pass
                self._io.write_f4le(self.f_albedo_blend2_color[i])

            for i in range(len(self.f_detail_normal_u_v_scale)):
                pass
                self._io.write_f4le(self.f_detail_normal_u_v_scale[i])

            for i in range(len(self.f_fresnel_legacy)):
                pass
                self._io.write_f4le(self.f_fresnel_legacy[i])

            for i in range(len(self.f_normal_mask_pow0)):
                pass
                self._io.write_f4le(self.f_normal_mask_pow0[i])

            for i in range(len(self.f_normal_mask_pow1)):
                pass
                self._io.write_f4le(self.f_normal_mask_pow1[i])

            for i in range(len(self.f_normal_mask_pow2)):
                pass
                self._io.write_f4le(self.f_normal_mask_pow2[i])

            for i in range(len(self.f_texture_blend_rate)):
                pass
                self._io.write_f4le(self.f_texture_blend_rate[i])

            for i in range(len(self.f_texture_blend_color)):
                pass
                self._io.write_f4le(self.f_texture_blend_color[i])



        def _check(self):
            pass
            if (len(self.f_albedo_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color", len(self.f_albedo_color), 3)
            for i in range(len(self.f_albedo_color)):
                pass

            if (len(self.f_albedo_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend_color", len(self.f_albedo_blend_color), 4)
            for i in range(len(self.f_albedo_blend_color)):
                pass

            if (len(self.f_parallax_max_sample) != 3):
                raise kaitaistruct.ConsistencyError(u"f_parallax_max_sample", len(self.f_parallax_max_sample), 3)
            for i in range(len(self.f_parallax_max_sample)):
                pass

            if (len(self.f_light_map_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_light_map_color", len(self.f_light_map_color), 4)
            for i in range(len(self.f_light_map_color)):
                pass

            if (len(self.f_thin_map_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_thin_map_color", len(self.f_thin_map_color), 3)
            for i in range(len(self.f_thin_map_color)):
                pass

            if (len(self.f_screen_uv_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_screen_uv_scale", len(self.f_screen_uv_scale), 2)
            for i in range(len(self.f_screen_uv_scale)):
                pass

            if (len(self.f_screen_uv_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_screen_uv_offset", len(self.f_screen_uv_offset), 2)
            for i in range(len(self.f_screen_uv_offset)):
                pass

            if (len(self.f_indirect_offset) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_offset", len(self.f_indirect_offset), 2)
            for i in range(len(self.f_indirect_offset)):
                pass

            if (len(self.f_indirect_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_indirect_scale", len(self.f_indirect_scale), 2)
            for i in range(len(self.f_indirect_scale)):
                pass

            if (len(self.f_fresnel_schlick_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_fresnel_schlick_rgb", len(self.f_fresnel_schlick_rgb), 3)
            for i in range(len(self.f_fresnel_schlick_rgb)):
                pass

            if (len(self.f_specular_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color", len(self.f_specular_color), 3)
            for i in range(len(self.f_specular_color)):
                pass

            if (len(self.f_emission_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_emission_color", len(self.f_emission_color), 3)
            for i in range(len(self.f_emission_color)):
                pass

            if (len(self.f_constant_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_constant_color", len(self.f_constant_color), 4)
            for i in range(len(self.f_constant_color)):
                pass

            if (len(self.f_roughness_rgb) != 3):
                raise kaitaistruct.ConsistencyError(u"f_roughness_rgb", len(self.f_roughness_rgb), 3)
            for i in range(len(self.f_roughness_rgb)):
                pass

            if (len(self.f_anisotoropic_direction) != 3):
                raise kaitaistruct.ConsistencyError(u"f_anisotoropic_direction", len(self.f_anisotoropic_direction), 3)
            for i in range(len(self.f_anisotoropic_direction)):
                pass

            if (len(self.f_anistropic_uv) != 2):
                raise kaitaistruct.ConsistencyError(u"f_anistropic_uv", len(self.f_anistropic_uv), 2)
            for i in range(len(self.f_anistropic_uv)):
                pass

            if (len(self.f_primary_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_primary_color", len(self.f_primary_color), 4)
            for i in range(len(self.f_primary_color)):
                pass

            if (len(self.f_secondary_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_secondary_color", len(self.f_secondary_color), 4)
            for i in range(len(self.f_secondary_color)):
                pass

            if (len(self.f_albedo_color2) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_color2", len(self.f_albedo_color2), 4)
            for i in range(len(self.f_albedo_color2)):
                pass

            if (len(self.f_specular_color2) != 3):
                raise kaitaistruct.ConsistencyError(u"f_specular_color2", len(self.f_specular_color2), 3)
            for i in range(len(self.f_specular_color2)):
                pass

            if (len(self.f_shininess2) != 4):
                raise kaitaistruct.ConsistencyError(u"f_shininess2", len(self.f_shininess2), 4)
            for i in range(len(self.f_shininess2)):
                pass

            if (len(self.f_transparency_clip_threshold) != 4):
                raise kaitaistruct.ConsistencyError(u"f_transparency_clip_threshold", len(self.f_transparency_clip_threshold), 4)
            for i in range(len(self.f_transparency_clip_threshold)):
                pass

            if (len(self.f_normal_power) != 3):
                raise kaitaistruct.ConsistencyError(u"f_normal_power", len(self.f_normal_power), 3)
            for i in range(len(self.f_normal_power)):
                pass

            if (len(self.f_albedo_blend2_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_albedo_blend2_color", len(self.f_albedo_blend2_color), 4)
            for i in range(len(self.f_albedo_blend2_color)):
                pass

            if (len(self.f_detail_normal_u_v_scale) != 2):
                raise kaitaistruct.ConsistencyError(u"f_detail_normal_u_v_scale", len(self.f_detail_normal_u_v_scale), 2)
            for i in range(len(self.f_detail_normal_u_v_scale)):
                pass

            if (len(self.f_fresnel_legacy) != 2):
                raise kaitaistruct.ConsistencyError(u"f_fresnel_legacy", len(self.f_fresnel_legacy), 2)
            for i in range(len(self.f_fresnel_legacy)):
                pass

            if (len(self.f_normal_mask_pow0) != 4):
                raise kaitaistruct.ConsistencyError(u"f_normal_mask_pow0", len(self.f_normal_mask_pow0), 4)
            for i in range(len(self.f_normal_mask_pow0)):
                pass

            if (len(self.f_normal_mask_pow1) != 4):
                raise kaitaistruct.ConsistencyError(u"f_normal_mask_pow1", len(self.f_normal_mask_pow1), 4)
            for i in range(len(self.f_normal_mask_pow1)):
                pass

            if (len(self.f_normal_mask_pow2) != 4):
                raise kaitaistruct.ConsistencyError(u"f_normal_mask_pow2", len(self.f_normal_mask_pow2), 4)
            for i in range(len(self.f_normal_mask_pow2)):
                pass

            if (len(self.f_texture_blend_rate) != 4):
                raise kaitaistruct.ConsistencyError(u"f_texture_blend_rate", len(self.f_texture_blend_rate), 4)
            for i in range(len(self.f_texture_blend_rate)):
                pass

            if (len(self.f_texture_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_texture_blend_color", len(self.f_texture_blend_color), 4)
            for i in range(len(self.f_texture_blend_color)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 480
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_resources = False
            self.resources__to_write = True
            self._should_write_anims = False
            self.anims__to_write = True

        def _read(self):
            self.type_hash = self._io.read_u4le()
            self.name_hash_crcjam32 = self._io.read_u4le()
            self.cmd_buffer_size = self._io.read_u4le()
            self.blend_state_hash = self._io.read_u4le()
            self.depth_stencil_state_hash = self._io.read_u4le()
            self.rasterizer_state_hash = self._io.read_u4le()
            self.num_resources = self._io.read_bits_int_le(12)
            self.reserverd1 = self._io.read_bits_int_le(9)
            self.id = self._io.read_bits_int_le(8)
            self.fog = self._io.read_bits_int_le(1) != 0
            self.tangent = self._io.read_bits_int_le(1) != 0
            self.half_lambert = self._io.read_bits_int_le(1) != 0
            self.stencil_ref = self._io.read_bits_int_le(8)
            self.alphatest_ref = self._io.read_bits_int_le(8)
            self.polygon_offset = self._io.read_bits_int_le(4)
            self.alphatest = self._io.read_bits_int_le(1) != 0
            self.alphatest_func = self._io.read_bits_int_le(3)
            self.draw_pass = self._io.read_bits_int_le(5)
            self.layer_id = self._io.read_bits_int_le(2)
            self.deffered_lighting = self._io.read_bits_int_le(1) != 0
            self.blend_factor = []
            for i in range(4):
                self.blend_factor.append(self._io.read_f4le())

            self.anim_data_size = self._io.read_u4le()
            self.ofs_cmd = self._io.read_u4le()
            self.ofs_anim_data = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.blend_factor)):
                pass

            _ = self.resources
            for i in range(len(self._m_resources)):
                pass
                self.resources[i]._fetch_instances()

            if (self.anim_data_size != 0):
                pass
                _ = self.anims
                self.anims._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.Material, self)._write__seq(io)
            self._should_write_resources = self.resources__to_write
            self._should_write_anims = self.anims__to_write
            self._io.write_u4le(self.type_hash)
            self._io.write_u4le(self.name_hash_crcjam32)
            self._io.write_u4le(self.cmd_buffer_size)
            self._io.write_u4le(self.blend_state_hash)
            self._io.write_u4le(self.depth_stencil_state_hash)
            self._io.write_u4le(self.rasterizer_state_hash)
            self._io.write_bits_int_le(12, self.num_resources)
            self._io.write_bits_int_le(9, self.reserverd1)
            self._io.write_bits_int_le(8, self.id)
            self._io.write_bits_int_le(1, int(self.fog))
            self._io.write_bits_int_le(1, int(self.tangent))
            self._io.write_bits_int_le(1, int(self.half_lambert))
            self._io.write_bits_int_le(8, self.stencil_ref)
            self._io.write_bits_int_le(8, self.alphatest_ref)
            self._io.write_bits_int_le(4, self.polygon_offset)
            self._io.write_bits_int_le(1, int(self.alphatest))
            self._io.write_bits_int_le(3, self.alphatest_func)
            self._io.write_bits_int_le(5, self.draw_pass)
            self._io.write_bits_int_le(2, self.layer_id)
            self._io.write_bits_int_le(1, int(self.deffered_lighting))
            for i in range(len(self.blend_factor)):
                pass
                self._io.write_f4le(self.blend_factor[i])

            self._io.write_u4le(self.anim_data_size)
            self._io.write_u4le(self.ofs_cmd)
            self._io.write_u4le(self.ofs_anim_data)


        def _check(self):
            pass
            if (len(self.blend_factor) != 4):
                raise kaitaistruct.ConsistencyError(u"blend_factor", len(self.blend_factor), 4)
            for i in range(len(self.blend_factor)):
                pass


        @property
        def resources(self):
            if self._should_write_resources:
                self._write_resources()
            if hasattr(self, '_m_resources'):
                return self._m_resources

            _pos = self._io.pos()
            self._io.seek(self.ofs_cmd)
            self._m_resources = []
            for i in range(self.num_resources):
                _t__m_resources = Mrl.ResourceBinding(self._io, self, self._root)
                _t__m_resources._read()
                self._m_resources.append(_t__m_resources)

            self._io.seek(_pos)
            return getattr(self, '_m_resources', None)

        @resources.setter
        def resources(self, v):
            self._m_resources = v

        def _write_resources(self):
            self._should_write_resources = False
            _pos = self._io.pos()
            self._io.seek(self.ofs_cmd)
            for i in range(len(self._m_resources)):
                pass
                self.resources[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_resources(self):
            pass
            if (len(self.resources) != self.num_resources):
                raise kaitaistruct.ConsistencyError(u"resources", len(self.resources), self.num_resources)
            for i in range(len(self._m_resources)):
                pass
                if self.resources[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"resources", self.resources[i]._root, self._root)
                if self.resources[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"resources", self.resources[i]._parent, self)


        @property
        def anims(self):
            if self._should_write_anims:
                self._write_anims()
            if hasattr(self, '_m_anims'):
                return self._m_anims

            if (self.anim_data_size != 0):
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_anim_data)
                self._m_anims = Mrl.AnimData(self._io, self, self._root)
                self._m_anims._read()
                self._io.seek(_pos)

            return getattr(self, '_m_anims', None)

        @anims.setter
        def anims(self, v):
            self._m_anims = v

        def _write_anims(self):
            self._should_write_anims = False
            if (self.anim_data_size != 0):
                pass
                _pos = self._io.pos()
                self._io.seek(self.ofs_anim_data)
                self.anims._write__seq(self._io)
                self._io.seek(_pos)



        def _check_anims(self):
            pass
            if (self.anim_data_size != 0):
                pass
                if self.anims._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"anims", self.anims._root, self._root)
                if self.anims._parent != self:
                    raise kaitaistruct.ConsistencyError(u"anims", self.anims._parent, self)


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 60
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimType1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.unk_01 = []
            for i in range(4):
                self.unk_01.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.unk_01)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimType1, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            for i in range(len(self.unk_01)):
                pass
                self._io.write_f4le(self.unk_01[i])



        def _check(self):
            pass
            if (len(self.unk_01) != 4):
                raise kaitaistruct.ConsistencyError(u"unk_01", len(self.unk_01), 4)
            for i in range(len(self.unk_01)):
                pass



    class CbAppClipPlane1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_plane_normal = []
            for i in range(3):
                self.f_plane_normal.append(self._io.read_f4le())

            self.padding_1 = self._io.read_f4le()
            self.f_plane_point = []
            for i in range(3):
                self.f_plane_point.append(self._io.read_f4le())

            self.padding_2 = self._io.read_f4le()
            self.f_app_clip_mask = self._io.read_f4le()
            self.padding_3 = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.f_plane_normal)):
                pass

            for i in range(len(self.f_plane_point)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbAppClipPlane1, self)._write__seq(io)
            for i in range(len(self.f_plane_normal)):
                pass
                self._io.write_f4le(self.f_plane_normal[i])

            self._io.write_f4le(self.padding_1)
            for i in range(len(self.f_plane_point)):
                pass
                self._io.write_f4le(self.f_plane_point[i])

            self._io.write_f4le(self.padding_2)
            self._io.write_f4le(self.f_app_clip_mask)
            self._io.write_f4le(self.padding_3)


        def _check(self):
            pass
            if (len(self.f_plane_normal) != 3):
                raise kaitaistruct.ConsistencyError(u"f_plane_normal", len(self.f_plane_normal), 3)
            for i in range(len(self.f_plane_normal)):
                pass

            if (len(self.f_plane_point) != 3):
                raise kaitaistruct.ConsistencyError(u"f_plane_point", len(self.f_plane_point), 3)
            for i in range(len(self.f_plane_point)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 48
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimSubEntry6(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(4):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range(self._parent.info.num_entry):
                _t_values = Mrl.AnimType6(self._io, self, self._root)
                _t_values._read()
                self.values.append(_t_values)



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass
                self.values[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry6, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self.values[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.header) != 4):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 4)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != self._parent.info.num_entry):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), self._parent.info.num_entry)
            for i in range(len(self.values)):
                pass
                if self.values[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._root, self._root)
                if self.values[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._parent, self)



    class CbOutlineEx1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_outline_outer_color = []
            for i in range(4):
                self.f_outline_outer_color.append(self._io.read_f4le())

            self.f_outline_inner_color = []
            for i in range(4):
                self.f_outline_inner_color.append(self._io.read_f4le())

            self.f_outline_balance_offset = self._io.read_f4le()
            self.f_outline_balance_scale = self._io.read_f4le()
            self.f_outline_balance = self._io.read_f4le()
            self.padding = self._io.read_f4le()
            self.f_outline_blend_mask = []
            for i in range(4):
                self.f_outline_blend_mask.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.f_outline_outer_color)):
                pass

            for i in range(len(self.f_outline_inner_color)):
                pass

            for i in range(len(self.f_outline_blend_mask)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbOutlineEx1, self)._write__seq(io)
            for i in range(len(self.f_outline_outer_color)):
                pass
                self._io.write_f4le(self.f_outline_outer_color[i])

            for i in range(len(self.f_outline_inner_color)):
                pass
                self._io.write_f4le(self.f_outline_inner_color[i])

            self._io.write_f4le(self.f_outline_balance_offset)
            self._io.write_f4le(self.f_outline_balance_scale)
            self._io.write_f4le(self.f_outline_balance)
            self._io.write_f4le(self.padding)
            for i in range(len(self.f_outline_blend_mask)):
                pass
                self._io.write_f4le(self.f_outline_blend_mask[i])



        def _check(self):
            pass
            if (len(self.f_outline_outer_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_outline_outer_color", len(self.f_outline_outer_color), 4)
            for i in range(len(self.f_outline_outer_color)):
                pass

            if (len(self.f_outline_inner_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_outline_inner_color", len(self.f_outline_inner_color), 4)
            for i in range(len(self.f_outline_inner_color)):
                pass

            if (len(self.f_outline_blend_mask) != 4):
                raise kaitaistruct.ConsistencyError(u"f_outline_blend_mask", len(self.f_outline_blend_mask), 4)
            for i in range(len(self.f_outline_blend_mask)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 64
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class CbBurnEmission1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_b_emission_factor = self._io.read_f4le()
            self.f_b_emission_alpha_band = self._io.read_f4le()
            self.padding_1 = []
            for i in range(2):
                self.padding_1.append(self._io.read_f4le())

            self.f_burn_emission_color = []
            for i in range(3):
                self.f_burn_emission_color.append(self._io.read_f4le())

            self.padding_2 = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.padding_1)):
                pass

            for i in range(len(self.f_burn_emission_color)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbBurnEmission1, self)._write__seq(io)
            self._io.write_f4le(self.f_b_emission_factor)
            self._io.write_f4le(self.f_b_emission_alpha_band)
            for i in range(len(self.padding_1)):
                pass
                self._io.write_f4le(self.padding_1[i])

            for i in range(len(self.f_burn_emission_color)):
                pass
                self._io.write_f4le(self.f_burn_emission_color[i])

            self._io.write_f4le(self.padding_2)


        def _check(self):
            pass
            if (len(self.padding_1) != 2):
                raise kaitaistruct.ConsistencyError(u"padding_1", len(self.padding_1), 2)
            for i in range(len(self.padding_1)):
                pass

            if (len(self.f_burn_emission_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_burn_emission_color", len(self.f_burn_emission_color), 3)
            for i in range(len(self.f_burn_emission_color)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 32
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.entry_count = self._io.read_u4le()
            self.ofs_to_info = []
            for i in range(self.entry_count):
                _t_ofs_to_info = Mrl.AnimOfs(self._io, self, self._root)
                _t_ofs_to_info._read()
                self.ofs_to_info.append(_t_ofs_to_info)



        def _fetch_instances(self):
            pass
            for i in range(len(self.ofs_to_info)):
                pass
                self.ofs_to_info[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.AnimData, self)._write__seq(io)
            self._io.write_u4le(self.entry_count)
            for i in range(len(self.ofs_to_info)):
                pass
                self.ofs_to_info[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.ofs_to_info) != self.entry_count):
                raise kaitaistruct.ConsistencyError(u"ofs_to_info", len(self.ofs_to_info), self.entry_count)
            for i in range(len(self.ofs_to_info)):
                pass
                if self.ofs_to_info[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"ofs_to_info", self.ofs_to_info[i]._root, self._root)
                if self.ofs_to_info[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"ofs_to_info", self.ofs_to_info[i]._parent, self)


        @property
        def ofs_base(self):
            if hasattr(self, '_m_ofs_base'):
                return self._m_ofs_base

            self._m_ofs_base = self._parent.ofs_anim_data
            return getattr(self, '_m_ofs_base', None)

        def _invalidate_ofs_base(self):
            del self._m_ofs_base

    class OfsBuff(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.ofs_const_buff = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.OfsBuff, self)._write__seq(io)
            self._io.write_u4le(self.ofs_const_buff)


        def _check(self):
            pass


    class CbVertexDisplacement2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev1":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re6":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"re0":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            elif _on == u"rev2":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbVertexDisplacement2, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev1":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re6":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"re0":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            elif _on == u"rev2":
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbVertexDisplacement21(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"re1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev1":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re6":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"re0":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            elif _on == u"rev2":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"re1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev1":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re6":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"re0":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            elif _on == u"rev2":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class TexOffset(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.texture_id = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Mrl.TexOffset, self)._write__seq(io)
            self._io.write_u4le(self.texture_id)


        def _check(self):
            pass


    class CbDdMaterialParam1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_dd_material_blend_color = []
            for i in range(4):
                self.f_dd_material_blend_color.append(self._io.read_f4le())

            self.f_dd_material_color_blend_rate = []
            for i in range(2):
                self.f_dd_material_color_blend_rate.append(self._io.read_f4le())

            self.f_dd_material_area_mask = []
            for i in range(2):
                self.f_dd_material_area_mask.append(self._io.read_f4le())

            self.f_dd_material_border_blend_mask = []
            for i in range(4):
                self.f_dd_material_border_blend_mask.append(self._io.read_f4le())

            self.f_dd_material_border_shade_band = self._io.read_f4le()
            self.f_dd_material_base_power = self._io.read_f4le()
            self.f_dd_material_normal_blend_rate = self._io.read_f4le()
            self.f_dd_material_reflect_blend_color = self._io.read_f4le()
            self.f_dd_material_specular_factor = self._io.read_f4le()
            self.f_dd_material_specular_map_factor = self._io.read_f4le()
            self.f_dd_material_env_map_blend_color = self._io.read_f4le()
            self.f_dd_material_area_alpha = self._io.read_f4le()
            self.f_dd_material_area_pos = []
            for i in range(4):
                self.f_dd_material_area_pos.append(self._io.read_f4le())

            self.f_dd_material_albedo_uv_scale = self._io.read_f4le()
            self.f_dd_material_normal_uv_scale = self._io.read_f4le()
            self.f_dd_material_normal_power = self._io.read_f4le()
            self.f_dd_material_base_env_map_power = self._io.read_f4le()
            self.f_dd_material_lantern_color = []
            for i in range(3):
                self.f_dd_material_lantern_color.append(self._io.read_f4le())

            self.padding_1 = self._io.read_f4le()
            self.f_dd_material_lantern_pos = []
            for i in range(3):
                self.f_dd_material_lantern_pos.append(self._io.read_f4le())

            self.padding_2 = self._io.read_f4le()
            self.f_dd_material_lantern_param = []
            for i in range(3):
                self.f_dd_material_lantern_param.append(self._io.read_f4le())

            self.padding_3 = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.f_dd_material_blend_color)):
                pass

            for i in range(len(self.f_dd_material_color_blend_rate)):
                pass

            for i in range(len(self.f_dd_material_area_mask)):
                pass

            for i in range(len(self.f_dd_material_border_blend_mask)):
                pass

            for i in range(len(self.f_dd_material_area_pos)):
                pass

            for i in range(len(self.f_dd_material_lantern_color)):
                pass

            for i in range(len(self.f_dd_material_lantern_pos)):
                pass

            for i in range(len(self.f_dd_material_lantern_param)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbDdMaterialParam1, self)._write__seq(io)
            for i in range(len(self.f_dd_material_blend_color)):
                pass
                self._io.write_f4le(self.f_dd_material_blend_color[i])

            for i in range(len(self.f_dd_material_color_blend_rate)):
                pass
                self._io.write_f4le(self.f_dd_material_color_blend_rate[i])

            for i in range(len(self.f_dd_material_area_mask)):
                pass
                self._io.write_f4le(self.f_dd_material_area_mask[i])

            for i in range(len(self.f_dd_material_border_blend_mask)):
                pass
                self._io.write_f4le(self.f_dd_material_border_blend_mask[i])

            self._io.write_f4le(self.f_dd_material_border_shade_band)
            self._io.write_f4le(self.f_dd_material_base_power)
            self._io.write_f4le(self.f_dd_material_normal_blend_rate)
            self._io.write_f4le(self.f_dd_material_reflect_blend_color)
            self._io.write_f4le(self.f_dd_material_specular_factor)
            self._io.write_f4le(self.f_dd_material_specular_map_factor)
            self._io.write_f4le(self.f_dd_material_env_map_blend_color)
            self._io.write_f4le(self.f_dd_material_area_alpha)
            for i in range(len(self.f_dd_material_area_pos)):
                pass
                self._io.write_f4le(self.f_dd_material_area_pos[i])

            self._io.write_f4le(self.f_dd_material_albedo_uv_scale)
            self._io.write_f4le(self.f_dd_material_normal_uv_scale)
            self._io.write_f4le(self.f_dd_material_normal_power)
            self._io.write_f4le(self.f_dd_material_base_env_map_power)
            for i in range(len(self.f_dd_material_lantern_color)):
                pass
                self._io.write_f4le(self.f_dd_material_lantern_color[i])

            self._io.write_f4le(self.padding_1)
            for i in range(len(self.f_dd_material_lantern_pos)):
                pass
                self._io.write_f4le(self.f_dd_material_lantern_pos[i])

            self._io.write_f4le(self.padding_2)
            for i in range(len(self.f_dd_material_lantern_param)):
                pass
                self._io.write_f4le(self.f_dd_material_lantern_param[i])

            self._io.write_f4le(self.padding_3)


        def _check(self):
            pass
            if (len(self.f_dd_material_blend_color) != 4):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_blend_color", len(self.f_dd_material_blend_color), 4)
            for i in range(len(self.f_dd_material_blend_color)):
                pass

            if (len(self.f_dd_material_color_blend_rate) != 2):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_color_blend_rate", len(self.f_dd_material_color_blend_rate), 2)
            for i in range(len(self.f_dd_material_color_blend_rate)):
                pass

            if (len(self.f_dd_material_area_mask) != 2):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_area_mask", len(self.f_dd_material_area_mask), 2)
            for i in range(len(self.f_dd_material_area_mask)):
                pass

            if (len(self.f_dd_material_border_blend_mask) != 4):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_border_blend_mask", len(self.f_dd_material_border_blend_mask), 4)
            for i in range(len(self.f_dd_material_border_blend_mask)):
                pass

            if (len(self.f_dd_material_area_pos) != 4):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_area_pos", len(self.f_dd_material_area_pos), 4)
            for i in range(len(self.f_dd_material_area_pos)):
                pass

            if (len(self.f_dd_material_lantern_color) != 3):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_lantern_color", len(self.f_dd_material_lantern_color), 3)
            for i in range(len(self.f_dd_material_lantern_color)):
                pass

            if (len(self.f_dd_material_lantern_pos) != 3):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_lantern_pos", len(self.f_dd_material_lantern_pos), 3)
            for i in range(len(self.f_dd_material_lantern_pos)):
                pass

            if (len(self.f_dd_material_lantern_param) != 3):
                raise kaitaistruct.ConsistencyError(u"f_dd_material_lantern_param", len(self.f_dd_material_lantern_param), 3)
            for i in range(len(self.f_dd_material_lantern_param)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 160
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimEntry(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.unk_00 = self._io.read_u4le()
            self.info = Mrl.AnimInfo(self._io, self, self._root)
            self.info._read()
            self.ofs_list_entry1 = self._io.read_u4le()
            self.unk_hash = self._io.read_u4le()
            self.ofs_entry2 = []
            for i in range(self.info.num_entry2):
                _t_ofs_entry2 = Mrl.BlockOffset(self._io, self, self._root)
                _t_ofs_entry2._read()
                self.ofs_entry2.append(_t_ofs_entry2)

            self.set_buff_hash = []
            for i in range(self.info.num_entry1):
                self.set_buff_hash.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            self.info._fetch_instances()
            for i in range(len(self.ofs_entry2)):
                pass
                self.ofs_entry2[i]._fetch_instances()

            for i in range(len(self.set_buff_hash)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimEntry, self)._write__seq(io)
            self._io.write_u4le(self.unk_00)
            self.info._write__seq(self._io)
            self._io.write_u4le(self.ofs_list_entry1)
            self._io.write_u4le(self.unk_hash)
            for i in range(len(self.ofs_entry2)):
                pass
                self.ofs_entry2[i]._write__seq(self._io)

            for i in range(len(self.set_buff_hash)):
                pass
                self._io.write_u4le(self.set_buff_hash[i])



        def _check(self):
            pass
            if self.info._root != self._root:
                raise kaitaistruct.ConsistencyError(u"info", self.info._root, self._root)
            if self.info._parent != self:
                raise kaitaistruct.ConsistencyError(u"info", self.info._parent, self)
            if (len(self.ofs_entry2) != self.info.num_entry2):
                raise kaitaistruct.ConsistencyError(u"ofs_entry2", len(self.ofs_entry2), self.info.num_entry2)
            for i in range(len(self.ofs_entry2)):
                pass
                if self.ofs_entry2[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"ofs_entry2", self.ofs_entry2[i]._root, self._root)
                if self.ofs_entry2[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"ofs_entry2", self.ofs_entry2[i]._parent, self)

            if (len(self.set_buff_hash) != self.info.num_entry1):
                raise kaitaistruct.ConsistencyError(u"set_buff_hash", len(self.set_buff_hash), self.info.num_entry1)
            for i in range(len(self.set_buff_hash)):
                pass



    class ResourceBinding(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_float_buffer = False
            self.float_buffer__to_write = True

        def _read(self):
            self.cmd_type = KaitaiStream.resolve_enum(Mrl.CmdType, self._io.read_bits_int_le(4))
            self.unused = self._io.read_bits_int_le(16)
            self.shader_obj_idx = self._io.read_bits_int_le(12)
            _on = self.cmd_type
            if _on == Mrl.CmdType.set_flag:
                pass
                self.value_cmd = Mrl.ShaderObject(self._io, self, self._root)
                self.value_cmd._read()
            elif _on == Mrl.CmdType.set_constant_buffer:
                pass
                self.value_cmd = Mrl.CmdOfsBuffer(self._io, self, self._root)
                self.value_cmd._read()
            elif _on == Mrl.CmdType.set_sampler_state:
                pass
                self.value_cmd = Mrl.ShaderObject(self._io, self, self._root)
                self.value_cmd._read()
            elif _on == Mrl.CmdType.set_texture:
                pass
                self.value_cmd = Mrl.CmdTexIdx(self._io, self, self._root)
                self.value_cmd._read()
            elif _on == Mrl.CmdType.set_unk:
                pass
                self.value_cmd = Mrl.ShaderObject(self._io, self, self._root)
                self.value_cmd._read()
            self.shader_object_id = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _on = self.cmd_type
            if _on == Mrl.CmdType.set_flag:
                pass
                self.value_cmd._fetch_instances()
            elif _on == Mrl.CmdType.set_constant_buffer:
                pass
                self.value_cmd._fetch_instances()
            elif _on == Mrl.CmdType.set_sampler_state:
                pass
                self.value_cmd._fetch_instances()
            elif _on == Mrl.CmdType.set_texture:
                pass
                self.value_cmd._fetch_instances()
            elif _on == Mrl.CmdType.set_unk:
                pass
                self.value_cmd._fetch_instances()
            if (self.cmd_type == Mrl.CmdType.set_constant_buffer):
                pass
                _ = self.float_buffer
                _on = self.shader_object_hash
                if _on == Mrl.ShaderObjectHash.cbuvrotationoffset:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbcolormask:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbspecularblend:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparam:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbdistortion:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbappreflectshadowlight:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparaminnercorrect:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbmaterial:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cboutlineex:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.globals:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbburnemission:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbappreflect:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbappclipplane:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbburncommon:
                    pass
                    self.float_buffer._fetch_instances()
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement2:
                    pass
                    self.float_buffer._fetch_instances()



        def _write__seq(self, io=None):
            super(Mrl.ResourceBinding, self)._write__seq(io)
            self._should_write_float_buffer = self.float_buffer__to_write
            self._io.write_bits_int_le(4, int(self.cmd_type))
            self._io.write_bits_int_le(16, self.unused)
            self._io.write_bits_int_le(12, self.shader_obj_idx)
            _on = self.cmd_type
            if _on == Mrl.CmdType.set_flag:
                pass
                self.value_cmd._write__seq(self._io)
            elif _on == Mrl.CmdType.set_constant_buffer:
                pass
                self.value_cmd._write__seq(self._io)
            elif _on == Mrl.CmdType.set_sampler_state:
                pass
                self.value_cmd._write__seq(self._io)
            elif _on == Mrl.CmdType.set_texture:
                pass
                self.value_cmd._write__seq(self._io)
            elif _on == Mrl.CmdType.set_unk:
                pass
                self.value_cmd._write__seq(self._io)
            self._io.write_u4le(self.shader_object_id)


        def _check(self):
            pass
            _on = self.cmd_type
            if _on == Mrl.CmdType.set_flag:
                pass
                if self.value_cmd._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._root, self._root)
                if self.value_cmd._parent != self:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._parent, self)
            elif _on == Mrl.CmdType.set_constant_buffer:
                pass
                if self.value_cmd._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._root, self._root)
                if self.value_cmd._parent != self:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._parent, self)
            elif _on == Mrl.CmdType.set_sampler_state:
                pass
                if self.value_cmd._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._root, self._root)
                if self.value_cmd._parent != self:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._parent, self)
            elif _on == Mrl.CmdType.set_texture:
                pass
                if self.value_cmd._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._root, self._root)
                if self.value_cmd._parent != self:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._parent, self)
            elif _on == Mrl.CmdType.set_unk:
                pass
                if self.value_cmd._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._root, self._root)
                if self.value_cmd._parent != self:
                    raise kaitaistruct.ConsistencyError(u"value_cmd", self.value_cmd._parent, self)

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 12
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_
        @property
        def shader_object_hash(self):
            if hasattr(self, '_m_shader_object_hash'):
                return self._m_shader_object_hash

            self._m_shader_object_hash = KaitaiStream.resolve_enum(Mrl.ShaderObjectHash, (self.shader_object_id >> 12))
            return getattr(self, '_m_shader_object_hash', None)

        def _invalidate_shader_object_hash(self):
            del self._m_shader_object_hash
        @property
        def float_buffer(self):
            if self._should_write_float_buffer:
                self._write_float_buffer()
            if hasattr(self, '_m_float_buffer'):
                return self._m_float_buffer

            if (self.cmd_type == Mrl.CmdType.set_constant_buffer):
                pass
                _pos = self._io.pos()
                self._io.seek((self._parent.ofs_cmd + self.value_cmd.ofs_float_buff))
                _on = self.shader_object_hash
                if _on == Mrl.ShaderObjectHash.cbuvrotationoffset:
                    pass
                    self._m_float_buffer = Mrl.CbUvRotationOffset(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement:
                    pass
                    self._m_float_buffer = Mrl.CbVertexDisplacement(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbcolormask:
                    pass
                    self._m_float_buffer = Mrl.CbColorMask(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbspecularblend:
                    pass
                    self._m_float_buffer = Mrl.CbSpecularBlend(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparam:
                    pass
                    self._m_float_buffer = Mrl.CbDdMaterialParam(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbdistortion:
                    pass
                    self._m_float_buffer = Mrl.CbDistortion(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbappreflectshadowlight:
                    pass
                    self._m_float_buffer = Mrl.CbAppReflectShadowLight(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparaminnercorrect:
                    pass
                    self._m_float_buffer = Mrl.CbDdMaterialParamInnerCorrect(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbmaterial:
                    pass
                    self._m_float_buffer = Mrl.CbMaterial(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cboutlineex:
                    pass
                    self._m_float_buffer = Mrl.CbOutlineEx(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.globals:
                    pass
                    self._m_float_buffer = Mrl.CbGlobals(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbburnemission:
                    pass
                    self._m_float_buffer = Mrl.CbBurnEmission(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbappreflect:
                    pass
                    self._m_float_buffer = Mrl.CbAppReflect(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbappclipplane:
                    pass
                    self._m_float_buffer = Mrl.CbAppClipPlane(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbburncommon:
                    pass
                    self._m_float_buffer = Mrl.CbBurnCommon(self._io, self, self._root)
                    self._m_float_buffer._read()
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement2:
                    pass
                    self._m_float_buffer = Mrl.CbVertexDisplacement2(self._io, self, self._root)
                    self._m_float_buffer._read()
                self._io.seek(_pos)

            return getattr(self, '_m_float_buffer', None)

        @float_buffer.setter
        def float_buffer(self, v):
            self._m_float_buffer = v

        def _write_float_buffer(self):
            self._should_write_float_buffer = False
            if (self.cmd_type == Mrl.CmdType.set_constant_buffer):
                pass
                _pos = self._io.pos()
                self._io.seek((self._parent.ofs_cmd + self.value_cmd.ofs_float_buff))
                _on = self.shader_object_hash
                if _on == Mrl.ShaderObjectHash.cbuvrotationoffset:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbcolormask:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbspecularblend:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparam:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbdistortion:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbappreflectshadowlight:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparaminnercorrect:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbmaterial:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cboutlineex:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.globals:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbburnemission:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbappreflect:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbappclipplane:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbburncommon:
                    pass
                    self.float_buffer._write__seq(self._io)
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement2:
                    pass
                    self.float_buffer._write__seq(self._io)
                self._io.seek(_pos)



        def _check_float_buffer(self):
            pass
            if (self.cmd_type == Mrl.CmdType.set_constant_buffer):
                pass
                _on = self.shader_object_hash
                if _on == Mrl.ShaderObjectHash.cbuvrotationoffset:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbcolormask:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbspecularblend:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparam:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbdistortion:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbappreflectshadowlight:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbddmaterialparaminnercorrect:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbmaterial:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cboutlineex:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.globals:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbburnemission:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbappreflect:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbappclipplane:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbburncommon:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)
                elif _on == Mrl.ShaderObjectHash.cbvertexdisplacement2:
                    pass
                    if self.float_buffer._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._root, self._root)
                    if self.float_buffer._parent != self:
                        raise kaitaistruct.ConsistencyError(u"float_buffer", self.float_buffer._parent, self)



    class CbAppReflectShadowLight1(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.f_app_reflect_shadow_dir = []
            for i in range(3):
                self.f_app_reflect_shadow_dir.append(self._io.read_f4le())

            self.padding = self._io.read_f4le()


        def _fetch_instances(self):
            pass
            for i in range(len(self.f_app_reflect_shadow_dir)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.CbAppReflectShadowLight1, self)._write__seq(io)
            for i in range(len(self.f_app_reflect_shadow_dir)):
                pass
                self._io.write_f4le(self.f_app_reflect_shadow_dir[i])

            self._io.write_f4le(self.padding)


        def _check(self):
            pass
            if (len(self.f_app_reflect_shadow_dir) != 3):
                raise kaitaistruct.ConsistencyError(u"f_app_reflect_shadow_dir", len(self.f_app_reflect_shadow_dir), 3)
            for i in range(len(self.f_app_reflect_shadow_dir)):
                pass


        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 16
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_

    class AnimSubEntry3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(24):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((16 * (self._parent.info.num_entry - 1))):
                self.values.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry3, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self._io.write_u1(self.values[i])



        def _check(self):
            pass
            if (len(self.header) != 24):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 24)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != (16 * (self._parent.info.num_entry - 1))):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), (16 * (self._parent.info.num_entry - 1)))
            for i in range(len(self.values)):
                pass



    class CbAppClipPlane(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_app_specific = False
            self.app_specific__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.app_specific
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._fetch_instances()
            else:
                pass
                self.app_specific._fetch_instances()


        def _write__seq(self, io=None):
            super(Mrl.CbAppClipPlane, self)._write__seq(io)
            self._should_write_app_specific = self.app_specific__to_write


        def _check(self):
            pass

        @property
        def app_specific(self):
            if self._should_write_app_specific:
                self._write_app_specific()
            if hasattr(self, '_m_app_specific'):
                return self._m_app_specific

            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self._m_app_specific = Mrl.CbAppClipPlane1(self._io, self, self._root)
                self._m_app_specific._read()
            else:
                pass
                self._m_app_specific = Mrl.CbAppClipPlane1(self._io, self, self._root)
                self._m_app_specific._read()
            self._io.seek(_pos)
            return getattr(self, '_m_app_specific', None)

        @app_specific.setter
        def app_specific(self, v):
            self._m_app_specific = v

        def _write_app_specific(self):
            self._should_write_app_specific = False
            _pos = self._io.pos()
            self._io.seek((self._parent._parent.ofs_cmd + self._parent.value_cmd.ofs_float_buff))
            _on = self._root.app_id
            if _on == u"dd":
                pass
                self.app_specific._write__seq(self._io)
            else:
                pass
                self.app_specific._write__seq(self._io)
            self._io.seek(_pos)


        def _check_app_specific(self):
            pass
            _on = self._root.app_id
            if _on == u"dd":
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)
            else:
                pass
                if self.app_specific._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._root, self._root)
                if self.app_specific._parent != self:
                    raise kaitaistruct.ConsistencyError(u"app_specific", self.app_specific._parent, self)


    class AnimSubEntry2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.header = []
            for i in range(12):
                self.header.append(self._io.read_u1())

            self.values = []
            for i in range((8 * self._parent.info.num_entry)):
                self.values.append(self._io.read_u1())



        def _fetch_instances(self):
            pass
            for i in range(len(self.header)):
                pass

            for i in range(len(self.values)):
                pass



        def _write__seq(self, io=None):
            super(Mrl.AnimSubEntry2, self)._write__seq(io)
            for i in range(len(self.header)):
                pass
                self._io.write_u1(self.header[i])

            for i in range(len(self.values)):
                pass
                self._io.write_u1(self.values[i])



        def _check(self):
            pass
            if (len(self.header) != 12):
                raise kaitaistruct.ConsistencyError(u"header", len(self.header), 12)
            for i in range(len(self.header)):
                pass

            if (len(self.values) != (8 * self._parent.info.num_entry)):
                raise kaitaistruct.ConsistencyError(u"values", len(self.values), (8 * self._parent.info.num_entry))
            for i in range(len(self.values)):
                pass



    @property
    def ofs_textures_calculated(self):
        if hasattr(self, '_m_ofs_textures_calculated'):
            return self._m_ofs_textures_calculated

        self._m_ofs_textures_calculated = 28
        return getattr(self, '_m_ofs_textures_calculated', None)

    def _invalidate_ofs_textures_calculated(self):
        del self._m_ofs_textures_calculated
    @property
    def ofs_materials_calculated(self):
        if hasattr(self, '_m_ofs_materials_calculated'):
            return self._m_ofs_materials_calculated

        self._m_ofs_materials_calculated = (self.ofs_textures_calculated + self.size_textures_)
        return getattr(self, '_m_ofs_materials_calculated', None)

    def _invalidate_ofs_materials_calculated(self):
        del self._m_ofs_materials_calculated
    @property
    def ofs_resources_calculated_no_padding(self):
        if hasattr(self, '_m_ofs_resources_calculated_no_padding'):
            return self._m_ofs_resources_calculated_no_padding

        self._m_ofs_resources_calculated_no_padding = ((self.size_top_level_ + self.size_textures_) + self.size_materials_)
        return getattr(self, '_m_ofs_resources_calculated_no_padding', None)

    def _invalidate_ofs_resources_calculated_no_padding(self):
        del self._m_ofs_resources_calculated_no_padding
    @property
    def size_todo_(self):
        if hasattr(self, '_m_size_todo_'):
            return self._m_size_todo_

        self._m_size_todo_ = ((self.size_top_level_ + self.size_textures_) + self.size_materials_)
        return getattr(self, '_m_size_todo_', None)

    def _invalidate_size_todo_(self):
        del self._m_size_todo_
    @property
    def size_textures_(self):
        if hasattr(self, '_m_size_textures_'):
            return self._m_size_textures_

        self._m_size_textures_ = (self.textures[0].size_ * self.num_textures)
        return getattr(self, '_m_size_textures_', None)

    def _invalidate_size_textures_(self):
        del self._m_size_textures_
    @property
    def size_top_level_(self):
        if hasattr(self, '_m_size_top_level_'):
            return self._m_size_top_level_

        self._m_size_top_level_ = 28
        return getattr(self, '_m_size_top_level_', None)

    def _invalidate_size_top_level_(self):
        del self._m_size_top_level_
    @property
    def size_materials_(self):
        if hasattr(self, '_m_size_materials_'):
            return self._m_size_materials_

        self._m_size_materials_ = (self.materials[0].size_ * self.num_materials)
        return getattr(self, '_m_size_materials_', None)

    def _invalidate_size_materials_(self):
        del self._m_size_materials_
    @property
    def ofs_resources_calculated(self):
        if hasattr(self, '_m_ofs_resources_calculated'):
            return self._m_ofs_resources_calculated

        self._m_ofs_resources_calculated = (self.ofs_resources_calculated_no_padding + (-(self.ofs_resources_calculated_no_padding) % 16))
        return getattr(self, '_m_ofs_resources_calculated', None)

    def _invalidate_ofs_resources_calculated(self):
        del self._m_ofs_resources_calculated

