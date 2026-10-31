MT_PROP_TYPES_RE5 = {  # Same in DMC4 PC
    "TYPE_UNDEFINED": 0,
    "TYPE_CLASS": 1,
    "TYPE_CLASSREF": 2,
    "TYPE_BOOL": 3,
    "TYPE_U8": 4,
    "TYPE_U16": 5,
    "TYPE_U32": 6,
    "TYPE_U64": 7,
    "TYPE_S8": 8,
    "TYPE_S16": 9,
    "TYPE_S32": 10,
    "TYPE_S64": 11,
    "TYPE_F32": 12,
    "TYPE_F64": 13,
    "TYPE_STRING": 14,
    "TYPE_COLOR": 15,
    "TYPE_POINT": 16,
    "TYPE_SIZE": 17,
    "TYPE_RECT": 18,
    "TYPE_MATRIX": 19,
    "TYPE_VECTOR3": 20,
    "TYPE_VECTOR4": 21,
    "TYPE_QUATERNION": 22,
    "TYPE_PROPERTY": 23,
    "TYPE_EVENT": 24,
    "TYPE_GROUP": 25,
    "TYPE_PAGE_BEGIN": 26,
    "TYPE_PAGE_END": 27,
    "TYPE_EVENT32": 28,
    "TYPE_ARRAY": 29,
    "TYPE_PROPERTYLIST": 30,
    "TYPE_GROUP_END": 31,
    "TYPE_CSTRING": 32,
    "TYPE_TIME": 33,
    "TYPE_FLOAT2": 34,
    "TYPE_FLOAT3": 35,
    "TYPE_FLOAT4": 36,
    "TYPE_FLOAT3x3": 37,
    "TYPE_FLOAT4x3": 38,
    "TYPE_FLOAT4x4": 39,
    "TYPE_EASECURVE": 40,
    "TYPE_LINE": 41,
    "TYPE_LINESEGMENT": 42,
    "TYPE_RAY": 43,
    "TYPE_PLANE": 44,
    "TYPE_SPHERE": 45,
    "TYPE_CAPSULE": 46,
    "TYPE_AABB": 47,
    "TYPE_OBB": 48,
    "TYPE_CYLINDER": 49,
    "TYPE_TRIANGLE": 50,
    "TYPE_CONE": 51,
    "TYPE_TORUS": 52,
    "TYPE_ELLIPSOID": 53,
    "TYPE_RANGE": 54,
    "TYPE_RANGEF": 55,
    "TYPE_RANGEU16": 56,
    "TYPE_HERMITECURVE": 57,
    "TYPE_CUSTOM": 58,
    "TYPE_END": 59,
}

REF_DTI_HASHES_RE5 = {  # hashes found in re5 files
    0x004F8CB6: 'uBioHazeFilter',
    0x01152EF8: 'uBioActorPL01Simple',
    0x0201006F: 'uLayoutSpr',
    0x07D496D4: 'sLightLinker::uSphere',
    0x0AA83FB2: 'sBioShader',
    0x0D3353F0: 'uBioShadow',
    0x0DD31DDC: 'uMotionCameraNoise',
    0x0F6FE858: 'uMovie',
    0x11A7E0D4: 'uDOFFilter',
    0x11EDABFE: 'uRadialBlurFilter',
    0x1265A094: 'uColorCorrectFilter',
    0x14A4CC49: 'uImagePlaneFilter',
    0x17B67883: 'uSpotMapLight',
    0x193EA064: 'uVolumeNoiseFilter',
    0x19F0ADDB: 'uBioActorPL00Face',
    0x1CA9E6F4: 'uSoundSe',
    0x1CCC1FA1: 'uChainEx',
    0x1CEBEC6A: 'sPrim',
    0x1EC9902C: 'uModelSky',
    0x23817EF5: 'sBioSound',
    0x2490846B: 'uBioActorPL01Face',
    0x26B5C952: 'uEfCam',
    0x2762254C: 'uBioActorPL00Simple',
    0x2ED1A340: 'uScheduler',
    0x3101A0EE: 'sLightLinker::uLinker',
    0x3261A0A7: 'sCamera',
    0x3292CECC: 'uBioActorPlayer',
    0x32C23F37: 'uPointShadowLight',
    0x369C12D5: 'uColorFogFilter',
    0x37A39C92: 'uCuboidShadowLight',
    0x3A9B7358: 'uLightScatteringFilter',
    0x3C14AD49: 'uTVNoiseFilter',
    0x3C603F04: 'uBioActorModel',
    0x3D0BEF1A: 'uBioActorPawn',
    0x3E759F98: 'uBioActorPL00',
    0x3F49FAE2: 'uFeedbackBlurFilter',
    0x42412AD7: 'uEffectEmitter',
    0x430C857E: 'uEffect2D',
    0x433B3068: 'sBioEffect',
    0x43BCBC9C: 'uMotionBlurFilter',
    0x45A468EE: 'uModel',
    0x4972AF0E: 'uBioActorPL01',
    0x49A43F8E: 'uPointLight',
    0x4E25402F: 'uBioEffect',
    0x4E474F9F: 'sBioCamera',
    0x4F32DAB6: 'uRefWater',
    0x4F736118: 'uEffectVFR',
    0x54A47FFE: 'uBackLight',
    0x54A9C99C: 'uScrModel',
    0x54E6A16B: 'uBloomFilter',
    0x5723084B: 'uItemLight',
    0x59351470: 'uToneMapControl',
    0x5982031D: 'uInfiniteLight',
    0x5A4279D6: 'sVibration',
    0x5AC010E5: 'uCaption',
    0x60C10879: 'uHemiSphereLight',
    0x625A63B0: 'sLightLinker::uCapsule',
    0x64C00555: 'uFlickerLight',
    0x66B41222: 'uPLActor',
    0x6752005F: 'uCrossFadeFilter',
    0x6A2EC243: 'uSpotLight',
    0x6AB61A89: 'uOceanWater',
    0x6AE27F28: 'uMotionCamera',
    0x6B0F0748: 'uPLActorEm84',
    0x6B792EAB: 'uSpotShadow',
    0x6DF8B0F1: 'uBlurFilter',
    0x6E1556FD: 'sLightLinker::uAnimLight',
    0x6E73764C: 'sEventPlayer',
    0x704FE852: 'uToneMapFilter',
    0x70CC7783: 'uHazeFilter',
    0x70F98581: 'sLightLinker::uCuboid',
    0x716D87B2: 'uAfterimage',
    0x734A460B: 'uLt00',
    0x783DCB90: 'uPLCamera',
    0x785BD903: 'uNoiseFogFilter',
    0x7A88B67B: 'uScrModelUV',
    0x7AD567B0: 'uFishEyeFilter',
    0x7BD1A7DC: 'sBioVibration',
    0x7C0A7952: 'uIdCredit00',
    0x7E3DCC96: 'uCapsuleShadowLight',
    0xFF000000: 'Junk???'
}

"""DTI hash table for Devil May Cry 4 (2008 PC, DevilMayCry4_DX9.exe)"""

DTI_DMC4 = {
    0x00001541: "aRoom403::MyDTI",
    0x0003986A: "MtSerializer::OBJECTDATA",
    0x000DA93E: "MPARAM_VECTOR3",
    0x005F8E26: "rCloth::MyDTI",
    0x006F4D08: "rCnsChain",
    0x008290B1: "MtContact",
    0x0084D75A: "CellMSEnvPoint",
    0x00A25EE3: "MtGeometry::Type",
    0x00F1F69E: "uPlWpEbonyIvory",
    0x01162BE6: "rMotionSe",
    0x014E7871: "aMTGSTitle::MyDTI",
    0x01513D59: "aMissionBeginDemo",
    0x0155DCD4: "rEffectList::EFL_KEYFRAME_INDEX",
    0x016066DC: "uAdhesion::MyDTI",
    0x0181DF10: "uCapsuleShadowLight::MyDTI",
    0x01858AF5: "aMTGSBeginDemo::MyDTI",
    0x018ADBC7: "rSoundPackage::Split",
    0x0195C450: "uYouDied",  # pc-only
    0x019B9215: "sDip::MyDTI",
    0x019CDBD5: "uEffectEdit",
    0x01B92B31: "r2Texture::MyDTI",
    0x01D37491: "sArea::MyDTI",
    0x01D7A976: "uEffectEdit::WORK_SET_MODEL_KF",
    0x0209890F: "sTool::MyDTI",
    0x02303F28: "uEnvMap::MyDTI",
    0x023DB1C3: "MtCollada::Primitive",
    0x0242EDD7: "CellVideoOutDisplayMode",
    0x026C04F6: "rSoundCurveSet::MyDTI",
    0x027D3EEE: "CellFsDirent",
    0x02833703: "rEffectStrip",
    0x029CE78E: "rPlacementXml::RootTrack",
    0x029F355A: "rEffectSetData::ESD_SET_LENS_FLARE",
    0x02AFB7C0: "uEffect::WORK_HEAD",
    0x02BF8B52: "cCamPanData_0",
    0x02C1B702: "rSoundStreamRequestXml::ElementData",
    0x02E765D3: "uEffectEdit::WORK_MOVE_PATH_STRIP_WORK",
    0x02FA87AE: "sStylishCount::SREPETITION_GUARD",
    0x0315E81F: "rSoundDirectionalSet",  # pc-only
    0x0315F513: "kCollisionPoint",
    0x031F8368: "MtGeomLineSegment",
    0x0322F7E0: "MtQuaternion",
    0x0323778C: "CellGameDataStatSet",
    0x0328E34B: "sCollision::Node",
    0x032EBC22: "aRoom004::MyDTI",
    0x03368EE8: "uShadowLight",
    0x036E4D98: "EFC_PAT_LIST",
    0x037F0A23: "sPrim::PacketInfo",
    0x039162E5: "aRoom200::MyDTI",
    0x039D9FAF: "uGameOptions::MyDTI",
    0x03AFCB43: "rModel::MODEL_INFO",
    0x03C94D8A: "MtCollada::Optics::MyDTI",
    0x03D3CF8A: "uCollTest",
    0x03D5E69E: "aMissionTGS::MyDTI",
    0x03DC5804: "cCameraRail::MyDTI",
    0x03F1F881: "MtGeomOBB::MyDTI",
    0x03FC875E: "sDevil4Movie",  # pc-only
    0x041F38EC: "uEm030GroundCtrl::cGroundParam",  # pc-only
    0x042FFFC9: "rReverb::cReverbData",
    0x04348226: "rNavigationMeshDae::Polygon",  # pc-only
    0x0435758B: "MT_IF",
    0x043734FC: "aRoom998::MyDTI",
    0x043E9319: "uEffectVFR::Filter",
    0x044A1BBB: "aRoom407::MyDTI",
    0x045315A5: "rSoundSystemFileMSSPURS",
    0x0453C429: "uDemoIntervene",  # pc-only
    0x0457771F: "sWorkRate",
    0x045BEAA7: "rShader::HEADER",
    0x0468E958: "MtCollada::COLLADA",
    0x0469F31C: "rSchedulerXml::UnitTrack::MyDTI",
    0x0490E287: "sSoundN::ENTRY_COMMAND",
    0x049CECAD: "uSchedulerEdit",
    0x04BA87FE: "rEffectList::EFL_KEYFRAME_VECTOR",
    0x04C63C34: "uToneMapFilter::GlareDef",
    0x04C8AC4B: "_Mbstatet",
    0x04D4AA2A: "rSprAnm::MyDTI",
    0x04E8B67B: "cDbgWorkRate",
    0x04F0BA74: "_D3DSURFACE_DESC",
    0x0506E617: "sPad::PAD_DATA",
    0x0520F070: "uEmSample::MyDTI",
    0x05306CC3: "sPrim::Material::PrimType",
    0x053B93E7: "MtDefaultAllocator::MyDTI",
    0x054FDEE9: "inflate_mode",
    0x056A8508: "cCamRailData_0",
    0x056CEE4D: "MtSerializer::HEADER",
    0x056D7ED5: "rEffectStrip::VERTEX_PARAM",
    0x0587E888: "uSuperimpose",  # pc-only
    0x058DC69B: "rSoundPackage::Program",
    0x059A2F18: "rEffectList::EFL_PARTICLE_MODEL",
    0x05A00E33: "rArchive::CompressStream::MyDTI",
    0x05A4FA4F: "uPointShadowLight::MyDTI",
    0x05AB0162: "cBranchScript::MyDTI",
    0x05AB686E: "uCockSuji02",  # pc-only
    0x05CEB12D: "MtCollada::Material::MyDTI",
    0x05EE5120: "uPlShlTest2::MyDTI",
    0x0615C107: "uFilter::BLENDOP_TYPE",
    0x061FFC89: "rCollision::Triangle",
    0x0623D0D2: "cTrans::Technique::HEADER",
    0x065DE29C: "rEffectSetData::ESD_SET_LINE",
    0x06869489: "rSoundSegXml",  # pc-only
    0x06AB54CC: "rCharTbl::MyDTI",
    0x06B59CE2: "uEffectVFR::LIGHT_DATA",
    0x06B96075: "uEm018",
    0x06E09840: "sDevil4Tool::MyDTI",
    0x06EDA9D8: "uEmRange::MyDTI",
    0x070F9BD6: "MtGeometry_0::MyDTI",
    0x071F55A9: "MtSize",
    0x07316A31: "uEfctBlur::MyDTI",
    0x073E245E: "aM00Result::MyDTI",
    0x0764B2D8: "aRoom000::MyDTI",
    0x07836621: "uResultFigure",
    0x078DFC9C: "cThinkMgr::MyDTI",
    0x07B77A14: "MtCollada::Combiner",
    0x07B8BCDE: "rFacialAnimation",
    0x07BF473C: "cCnsChain::MyDTI",
    0x07C98643: "uEm013::MyDTI",
    0x07D7AA14: "rSchedulerXml::SystemTrack",
    0x07D9FEF2: "uPlayerDante::kMdlCoat",
    0x07DB6C1F: "aRoom204::MyDTI",
    0x07E43FF0: "rEffectSetData::ESD_LIFE_FRAME",
    0x07EBA80E: "uPlayer::kDevilTrg",
    0x08005726: "uPlayer::EFCT_TYPE",
    0x08040F0C: "std::_Ranit",
    0x082DB5B8: "MESS_QUEUE_INFO",
    0x083343D6: "rSoundSystemFile",
    0x0848445D: "uPauseSystems",
    0x08578F46: "sSoundN::StreamVoice::FADE_STATUS",
    0x0862E847: "uEm010",
    0x08630FBD: "cEnemyCreateData::MyDTI",
    0x088E1BC8: "cAttackStatus",
    0x089F619B: "kROUTEQ_OUT",
    0x08B55184: "sSoundN::DISTANCE_CURVE_TYPE",
    0x08C18985: "uEffectVFR::Generator",
    0x08E3F7CD: "rEffectSetData::ESD_SET_POLYGON",
    0x08EACF67: "code",
    0x09052149: "MtDataWriter::Label",
    0x0919B72D: "cTrans::VertexBuffer::MyDTI",
    0x0921C934: "uPlayerNero::kMdlHair",
    0x09319A33: "MtGeomTriangle",
    0x093A296B: "uCartridge::MyDTI",
    0x09418340: "uPlayer::kJumpData",
    0x094681A0: "uEm010::MyDTI",
    0x094C0C60: "ImitationBaseTexture",
    0x0951820A: "uMissionResult::MyDTI",
    0x095264F7: "rModel::MATERIAL_INFO",
    0x09546BFC: "aRoom207::MyDTI",
    0x09663108: "uPlayer::kCancelInfoBit",
    0x0967880B: "uPlayer::BODY_ID",
    0x0970E4AD: "uEffectEdit::WORK_SET_BILLBOARD",
    0x09A9580B: "rPlacementXml",
    0x09AF527C: "uScrView::MyDTI",
    0x09C40D96: "rArchive::CompressStream",
    0x09C4B494: "uMStartString1",  # pc-only
    0x09CB8ACF: "rSoundRequestXml",
    0x09EBB53B: "aRoom003::MyDTI",
    0x09EBE99B: "aDemoDigest",  # pc-only
    0x09ED06F6: "rEffectSetData::ESD_SET_MODEL_COMMON",
    0x09EE2245: "MtCollada::Scale::MyDTI",
    0x0A0A1DA1: "cTrans::MESH",
    0x0A1CE46C: "sTool_0",
    0x0A245BF8: "cLockOnTarget",
    0x0A3254E9: "fontMap_0::MyDTI",
    0x0A46D4CF: "sFile",
    0x0A52C7A8: "uPlShlTest",
    0x0A53A611: "aNative::MyDTI",
    0x0ABB64EB: "uLicence::MyDTI",
    0x0AC51C58: "aRoom404::MyDTI",
    0x0AC52B4B: "cJointHandler",  # pc-only
    0x0AC58757: "uPlayerNero::cDevilTrgAtckCheck",  # pc-only
    0x0ACDF089: "uFreeCamera::MyDTI",
    0x0B0E25F1: "rSchedulerXml::ObjectTrack",
    0x0B0F8B54: "uPlayer::kWindParam",
    0x0B210BA2: "kActionRnd",
    0x0B2AAC9A: "rAttributeSe",
    0x0B4B4CE7: "MtHeapArray",
    0x0B69909B: "cCameraRect3D",
    0x0B8530E2: "MtHalf",
    0x0B8B4F0B: "cCameraBase::MyDTI",
    0x0BB8A614: "uScreenMap::MyDTI",
    0x0BC44945: "mutex_attr",
    0x0BD3EF2E: "std::_Ctypevec",
    0x0BE08C53: "rClothXml::Index::MyDTI",
    0x0BEBB620: "PS3_REPLACE",
    0x0BF24085: "uPlayer::kMotionParam",
    0x0BF3DF3F: "uTgsControl::MyDTI",
    0x0C0926F1: "uPlayer::kBtnParam",
    0x0C14D9A5: "uFilter::MyDTI",
    0x0C189E0A: "rSoundRandom::MyDTI",
    0x0C19D386: "MtProperty::TYPE",
    0x0C1E1765: "sDevil4Tool",
    0x0C1F10BE: "sGpuParticle::MyDTI",
    0x0C29486C: "__vector_float",
    0x0C29A368: "uPlayer::kActLimitBit",
    0x0C3679FC: "rSoundSeg::SEG_HIT_DATA::MyDTI",
    0x0C3A6AC5: "sCollision::Node::MyDTI",
    0x0C3FD9B7: "sCollision::CallbackInfo",
    0x0C45C5D1: "aGameOver",  # pc-only
    0x0C60F961: "rEffectList::EFL_GENERATOR",
    0x0C6987AC: "uFilter::transImage::SCREEN_VERTEX",
    0x0C6AF2CA: "sSpu::MyDTI",
    0x0C6C7C85: "sRender::Pass::COUNTER_TYPE",
    0x0C6DAA48: "cTrans::IndexBuffer",
    0x0C853F5B: "rSchedulerXml::IntTrack",
    0x0C86C06C: "cSpline::MyDTI",
    0x0CCC3185: "sys_event_queue_attr",
    0x0CD86EB8: "uLight::MyDTI",
    0x0CF0A36D: "sprMapHead::MyDTI",
    0x0CF40CDF: "cPermitAttack::MyDTI",
    0x0D01E02F: "uPlayer::kPadBit",
    0x0D0A38C7: "HIT_MARK_ANGLE",
    0x0D1BE22A: "kActionRndTbl",
    0x0D1E6506: "aRoom203::MyDTI",
    0x0D28ADF9: "std::tm",
    0x0D2F1B69: "cShape::MyDTI",
    0x0D310A97: "uTitleC",  # pc-only
    0x0D5DF117: "uEmTest3::MyDTI",
    0x0DA1BBC1: "aRoom007::MyDTI",
    0x0DACA7BA: "MtSH",
    0x0DBF733D: "MtCollada::Controller",
    0x0DC037C6: "aM01EndDemo::MyDTI",
    0x0DC331F8: "rEffectList::EFL_PARTICLE_LENS_FLARE",
    0x0DCB996D: "cArea::MyDTI",
    0x0DD53842: "cTrans::CubeTexture::MyDTI",
    0x0DD65268: "uEfctJntRoute::Joint::MyDTI",
    0x0DED692D: "rEffectSetData::ESD_SET_FILTER",
    0x0DF49294: "aMissionResult",  # pc-only
    0x0DFB06D1: "rSoundSeg",
    0x0E252627: "uTgsControl",
    0x0E285DAB: "MtSerializer::XmlHandler",
    0x0E4F6C2B: "MtCollada::Input",
    0x0E51EBB8: "cDipData",
    0x0E58FD17: "cEventHitData",
    0x0E631AD1: "_D3DBLEND",
    0x0E844BED: "uLevelCorrectFilter",
    0x0E8F12A2: "aRoom400::MyDTI",
    0x0EB22BED: "MtGeomSphere",
    0x0EBC3CE5: "rMotionSe::MyDTI",
    0x0EC377F4: "rCollisionShape::MyDTI",
    0x0ECBBAA1: "rEffectSetData::ESD_MOVE_PATH_CHAIN_COLL",
    0x0ECD7DF4: "rSoundCurveSet",
    0x0ECDD188: "MtClipboardStream::MyDTI",
    0x0EEBAE36: "uModel::MaterialGroup",  # pc-only
    0x0F06F4BA: "uMinimap::transImage::SCREEN_VERTEX",
    0x0F1EB126: "MtCollada::Scene",
    0x0F33AF45: "cTrans::CMD_SCISSOR",
    0x0F458E1C: "uPlayer::kLockOnParam",
    0x0F4FF3FC: "rEffectSetData::ESD_MOVE_PATH_CHAIN",
    0x0F5EB8E6: "sDevil4Debug::MyDTI",
    0x0F625302: "MT_SETTER",
    0x0F64872D: "MtFilePath",
    0x0F6D7312: "uMirror::MyDTI",
    0x0F6DC816: "uShadow::MyDTI",
    0x0F8149A3: "sPrim::SCENECONTEXT",
    0x0FBBC08A: "rSchedulerXml::Track",
    0x0FC8402B: "cTrans::Element",
    0x0FEFC14F: "rSchedulerXml",
    0x0FF755B4: "rAttributeSeXml::MyDTI",
    0x101FA69B: "aRoom010::MyDTI",
    0x10377DD2: "MtRandom",
    0x1054EA21: "cMaterial::MyDTI",
    0x1072A82B: "uActorModel::Constraint::MyDTI",
    0x1077B3F5: "MtCollada::Array::MyDTI",
    0x107BC6D3: "uEffectEdit::WORK_MOVE_COLL_WORK",
    0x107DEE6C: "rDevilCamera",
    0x108DCE62: "cSchedulerPath",  # pc-only
    0x109D3A67: "rSchedulerXml::SchedulerTrack::MyDTI",
    0x10A0785C: "aRoom214::MyDTI",
    0x10A85963: "uEffectEdit::WORK_MOVE_PATH_COMMON",
    0x10A8D98E: "uItemGetCamera::MyDTI",
    0x10BAF136: "uEffectEdit::WORK_SET_PRIM_MODEL",
    0x10C460E6: "rMessage",
    0x10CDE52E: "uMStartString2",  # pc-only
    0x10CE27B4: "uMovie::MyDTI",
    0x10E13DEE: "RadixSort",
    0x10EB8175: "uTgsDemoComing::MyDTI",
    0x10F11674: "rSoundPackageXml::ProgramData",
    0x11061B10: "cActionMgr_0",
    0x110FAC13: "rEffectSetData::ESD_MOVE_PATH_STRIP",
    0x111777FC: "std::char_traits",
    0x111C956F: "sCollision::ContactDefine",
    0x1130FF80: "uDevil4Model::MyDTI",
    0x1152F40F: "uPlayer::ATCK_ATTR",
    0x115720C1: "MtCollada::Skew",
    0x116520C4: "uPlayer::kCmdHead",
    0x116BB9FD: "uEm013",
    0x1172D043: "cCollGroup",
    0x11745209: "kTHINKDATA",
    0x118505DA: "sResource::Property",
    0x118DBD7C: "ENEMY_ID",
    0x11A7E0D4: "uDOFFilter",
    0x11AC8E76: "MtPlane",
    0x11B406E0: "rPlParamTbl::MyDTI",
    0x11BF6DCC: "MtGeomCapsule::MyDTI",
    0x11C0061C: "uPlWpRedQueen::MyDTI",
    0x11C00989: "aRoom409::MyDTI",
    0x11C39651: "uShadowLight::MyDTI",
    0x11C6E908: "sCollision::Param",
    0x11CD02DC: "uEnemySetCtrl",
    0x11EDABFE: "uRadialBlurFilter",
    0x11F906B1: "uPlayer::CND_TYPE",
    0x11FBC512: "rEffectAnim::EAN_HEADER",
    0x1201A0BB: "MtColorF",
    0x12291A9F: "rDefendStatusData::MyDTI",
    0x123D8211: "rEffectSetData::ESD_MOVE_PATH_KEYFRAME",
    0x124D0300: "uFlatWater::WATER_VERTEX",
    0x124D648B: "rSoundStreamRequest::SOUND_STERAM_READ_TYPE",
    0x126AD8E0: "rMovie",
    0x126E63B3: "rEffectList::EFL_INDEX",
    0x1276393B: "rFacialAnimation::MyDTI",
    0x12A613C0: "MtMemoryCachedStream::MyDTI",
    0x12A6EAD9: "sPad::PAD_VIB_LIST",
    0x12B0F04A: "uEffectVFR::Polygon",
    0x12B39843: "cEventChgRoom::MyDTI",
    0x12BFAF39: "rSprAnm",
    0x12C90632: "rSoundEngine::EngineCurveData",  # pc-only
    0x12D2103E: "rEffectList::EFL_MOVE_MUL",
    0x12E51EE5: "MtCollada::Param::FLOW",
    0x12ED9B24: "sSoundN::MyDTI",
    0x12EDD5BA: "sDevil4Sound::DEVIL4_STREAM_SEARCH_KEY",
    0x12EDFA22: "uModel::RenderInfo::MyDTI",
    0x12EEAA66: "uEffectEdit::WORK_MOVE_MUL_KF",
    0x12EEADB6: "uGridEnvLight",  # pc-only
    0x12F53B5C: "cCnsIK",
    0x1318A835: "uEffectVFR::Model",
    0x13272207: "cTrans::SCENE",
    0x134CA400: "kCollisionSegment3",
    0x135A5AA3: "MtCollada::Image",
    0x136DF061: "rCloth::Header",
    0x137A22FA: "uCockSuji::MyDTI",
    0x13A070F2: "uModel::Constraint_0::MyDTI",
    0x13B512E3: "uCnsChainReset",  # pc-only
    0x13C5E4D0: "sDevil4Main",
    0x13C97C8C: "rEffectSetData::ESD_SET_MODEL",
    0x140786A1: "MtAllocator::TYPE",
    0x140A16A5: "std::_Lldiv_t",
    0x1416D07B: "MtCollada::Sampler::MyDTI",
    0x14190986: "cTrans::Technique",
    0x141EA251: "rPlacementXml::RefTrack",
    0x14324F60: "rSoundSourceMusicInterMediate",
    0x1436D3B6: "rEffectAnimation::EFA_HEADER",
    0x144FCF62: "EFC_PARAM_F32",
    0x14735482: "EFC_KEYFRAME_U16",
    0x14A4CC49: "uImagePlaneFilter",
    0x14AA843B: "uEffectEdit::MyDTI",
    0x14C3359A: "cTrans::CMD_ZPASS",
    0x14C5A5B9: "uEffectEdit::WORK_POS_CHAIN",
    0x14EA76A6: "aRoom210::MyDTI",
    0x15435600: "cCameraPan::MyDTI",
    0x154703ED: "uDevil4Effect",
    0x154BF9E0: "MtGeomAABB_0",
    0x1558AA53: "rEffectSetData::ESD_MOVE_MUL_COLL",
    0x155CCA88: "rLeafAnim::Index",  # pc-only
    0x1565A615: "cEventHit",
    0x15692485: "uFilter",
    0x157389D3: "rEffectSetDataList::ESL_SET_COMMON",
    0x157D8238: "aMlpzResult",  # pc-only
    0x15807B37: "MtCollada::Pass",
    0x15D7D262: "uEm011Test::MyDTI",
    0x15D8846F: "sPad::Pad",
    0x15EA92EE: "rSoundSourceSE::MyDTI",
    0x15ED010D: "uPlayer::cParamTblCtrl",  # pc-only
    0x15ED233C: "sSoundN::REVERB_PARAMETER",
    0x15F97B7D: "uLbrySelTitle",  # pc-only
    0x15FAFA20: "uPlayer::kBdyAction",
    0x16060B9E: "MtCollada::Perspective::MyDTI",
    0x16099A8B: "uEm019::MyDTI",
    0x160B847D: "MtCollada::Element::MyDTI",
    0x161A1299: "uEffectVFR::MoveNone",
    0x161A9537: "uSynchroPointLight::MyDTI",
    0x162C4EA7: "MtMemoryCachedStream",
    0x16320AB3: "uEffectEdit::WORK_MOVE_ADD_COLL",
    0x1638869C: "MtRangeU16",
    0x167A6809: "MtClipboardStream",
    0x167B5231: "aM01EndDemo",
    0x167DBBFF: "rSoundStreamRequest",
    0x169836B2: "MtCollisionGjk::MyDTI",
    0x1699BFBF: "aGameGrid",  # pc-only
    0x16C2EB54: "rSoundSystemFileMSSPURSInterMediate",
    0x16C9D9FD: "rSoundCurveSetXml::BasicCurves",
    0x16E240A8: "uViolence::MyDTI",
    0x16F98E75: "cCollisionGroup",
    0x17068A5D: "cCnsMatrix",  # pc-only
    0x1725138F: "MT_GETTER",
    0x173BDC18: "cEventHitData_0::MyDTI",
    0x1740B3C6: "rAttackStatusData::MyDTI",
    0x17482381: "sCollision::Collider::MyDTI",
    0x175F8B3C: "cTrans::Element::MyDTI",
    0x1760A6C7: "uPlayer::ATCK_LV",
    0x176DEE25: "rSchedulerXml::FloatTrack::Key::MyDTI",
    0x177C5CF0: "sShader::TechniqueDesc::MyDTI",
    0x179AFCEC: "uCustomDemoActor::MyDTI",
    0x17A2E63B: "cTrans::Technique::SHADER",
    0x17A44458: "rMotionSeXml::MyDTI",
    0x17A69ACE: "rMovieOnMemoryInterMediate",  # pc-only
    0x17AFA970: "sTool_0::OP_MODE",
    0x17B6A0C8: "uBPResultSuji",  # pc-only
    0x17B90F67: "uEffectEdit::WORK_MOVE_PATH_STRIP_COLL",
    0x17C54661: "rEffectSetData::ESD_SET_COMMON",
    0x17CC8F07: "cTrans::VertexDecl::MyDTI",
    0x17F411E7: "rModel::JOINT_INFO",
    0x180C7C20: "CellGameDataStatGet",
    0x180D4170: "cEventHit::MyDTI",
    0x180D7D56: "rSoundCurveSetXml::BasicCurves::MyDTI",
    0x182BA9F3: "aRoom009::MyDTI",
    0x18443F5E: "CellSpursJob128",
    0x187B49FE: "rSchedulerXml::VectorTrack::MyDTI",
    0x187BF8C0: "rCnsChain::cBONE_DATA",  # pc-only
    0x187DE4A0: "uFade::MyDTI",
    0x18819D3A: "rShapeWeight::SHAPE_WEIGHT",
    0x188837D2: "rSoundCurveSetXml::MyDTI",
    0x188CCCFE: "fontMap_0",
    0x18B215AE: "MtString",
    0x18D8A3AA: "cFootprintCtrl",  # pc-only
    0x18EA5867: "uArcLoader",  # pc-only
    0x1905CA67: "rSoundSystemFileMSSPURSInterMediate::MyDTI",
    0x1909B258: "EventInfo::PRIORITY",
    0x1922B54D: "rReverbXml",
    0x193EA064: "uVolumeNoiseFilter",
    0x1955176A: "rEffectSetData::ESD_SET_CULL_BILLBOARD",
    0x19557744: "uEffectEdit::WORK_POS_POLYGON",
    0x1963734E: "std::reverse_iterator",
    0x196D8EA8: "cCnsTest2",
    0x1972E80A: "rMotion::MyDTI",
    0x19909D49: "cCollision",
    0x19A1048A: "sSoundN::StreamEntry",
    0x19ACA8CC: "MtCollada::Shader",
    0x19BA339B: "MtXmlWriter",
    0x19BD59F8: "MtTriangle",
    0x19BEA516: "uModel2Light::MyDTI",
    0x19EAF1BF: "uUnitSerializeTestItem0::MyDTI",
    0x19FDF817: "sCapture::SCALE",
    0x1A0169FF: "uMessage",
    0x1A05554C: "uPointLight::MyDTI",
    0x1A09AB7B: "sSoundN::Listening",
    0x1A0BAB1B: "uFreeCamera",
    0x1A179265: "rPlacementXml::Track",
    0x1A1B67FC: "uEm022::cComboCtrl",  # pc-only
    0x1A1C9A9D: "rPlParamTbl",
    0x1A235B11: "uEffectVFR::POLYLINE_DATA",
    0x1A31C528: "aM01Result::MyDTI",
    0x1A3AB172: "sException",
    0x1A3CB1DF: "MtLineSegment",
    0x1A44C584: "uStream",  # pc-only
    0x1A4981DB: "rNavigationMeshDae::Mesh",  # pc-only
    0x1A657145: "aRoom213::MyDTI",
    0x1A65E0E6: "sMediator::MyDTI",
    0x1A801099: "kAction",
    0x1A838B92: "sShader::FUNC_SPECULAR",
    0x1A8E0469: "cShape",
    0x1AB06883: "uEffectVFR::MODEL_DATA",
    0x1AD8D8E7: "r2Texture::HEADER2",
    0x1AF46990: "MtCollisionGjk",
    0x1B07CF83: "MtFCurve::Key_0",
    0x1B1AC52E: "uEffectEdit::WORK_MOVE_MUL",
    0x1B2A37FA: "cTrans::CMD_CLIPPLANE",
    0x1B4BD3D8: "_D3DLOCKED_RECT",
    0x1B585399: "MtCollada::Extra",
    0x1B60C64D: "uToneCurveFilter::MyDTI",
    0x1B6A266D: "sMain::JOB_MODE",
    0x1B85C8B7: "uEffectVFR::Hit",
    0x1B8DFF77: "sPrim::DepthOrder",
    0x1B96F13B: "MtCollada::Sampler",
    0x1BB008E0: "cStageSetFlagMgr",  # pc-only
    0x1BC22EB2: "cCnsHand",
    0x1BC760C7: "uEffectVFR::MoveAdd",
    0x1BD3651C: "uPlayer::kTameParam",
    0x1BE2EEED: "uFlowingWater",
    0x1C06BDD1: "cThinkMgr",
    0x1C149EBF: "MtFCurve::Key::MyDTI",
    0x1C27D87C: "rSoundStreamRequest::Header",
    0x1C33CB09: "uCuboidShadowLight::MyDTI",
    0x1C393B03: "uSprLayout",
    0x1C4138EE: "MtDataWriter",
    0x1C66EA4E: "cSplinePoints_0::MyDTI",
    0x1C75DB9F: "MtFloat2",
    0x1C86562E: "cTrans::CMD_PRIM",
    0x1C8FF0ED: "uCnsOffset",
    0x1C99A409: "uDirectionalGlowFilter::MyDTI",
    0x1C9BA495: "MtArray::MyDTI",
    0x1CB34CE6: "uPlayer::POSE_ST",
    0x1CC9533E: "kCollisionTriangle",
    0x1CDDB1A4: "cCameraRect3D_0::MyDTI",
    0x1CDE79CE: "aRoom209::MyDTI",
    0x1CEA665F: "ANM_SEQUENCE",
    0x1CF2573A: "sCamera::Viewport::MyDTI",
    0x1CF29E9A: "cMaterial",
    0x1D043761: "sArea::AreaInfo::MyDTI",
    0x1D37CC33: "rPlacementXml::VectorTrack::MyDTI",
    0x1D6ADE5B: "MtHeapArray_0::MyDTI",
    0x1D7DA970: "MtMemoryStream::MyDTI",
    0x1DA91661: "uEm018BreakHouse",
    0x1DAF24F8: "rEffectList::EFL_LIFE_FRAME",
    0x1DCF02FE: "uTgsTrial::MyDTI",
    0x1DDAF882: "cDipData_0::MyDTI",
    0x1DDC3D81: "uTgsTitle",
    0x1E30542F: "uSeGenerator::MyDTI",
    0x1E30A837: "MtGeomOBB_0",
    0x1E3D95E3: "uEm000::MyDTI",
    0x1E4484C8: "cCollPrim",
    0x1E4F6977: "uActor::MyDTI",
    0x1E507963: "cConstraint::MyDTI",
    0x1E5BB8DB: "rSoundSystemFileMSDSPTimeDomainReverbInterMediate::MyDTI",
    0x1E6C772B: "MtCollada::Matrix",
    0x1E73BA03: "MOTION_INFO",
    0x1E8D6161: "sMain::PROCESS",
    0x1E8F0D9B: "uPlWpRightHand::MyDTI",
    0x1E96365F: "rEffectSetData::ESD_MOVE_PATH_KEYFRAME_COLL",
    0x1EA217A3: "uModelGlass",
    0x1EA959BF: "uScrView",
    0x1EA9B172: "rSoundSeg::LayoutInfo",
    0x1EE199FE: "rTexture::SHFACTOR",
    0x1EF2E233: "uEffectEdit::WORK_MOVE_ADD_COLL_KF",
    0x1F04BE4D: "uEm000Base",
    0x1F3422D8: "MtFileStream",
    0x1F46601D: "uToneMapFilter::GhostDef",
    0x1F4BE986: "MtTime",
    0x1F635FFB: "uCameraCtrl::MODE",
    0x1F669355: "aRoom::STATUS",
    0x1F6ED57D: "uTgsGameOver::MyDTI",
    0x1F79AD03: "uPlayer::cProcSpdCtrl",  # pc-only
    0x1F7F10B6: "sPad::Pad::MyDTI",
    0x1F82B805: "uEffectVFR::LensFlare",
    0x1FAC1680: "_CGprogram",
    0x1FB8D129: "uEffectEdit::WORK_SET_MODEL",
    0x1FBE1059: "MtBlockAllocator",  # pc-only
    0x1FBE4320: "cCharTblMgr::kCtJump",
    0x1FDBF9B5: "uShadow",
    0x1FDDBD73: "MtGeomMinkowskiSum::MyDTI",
    0x1FE72F93: "uEfctPlGrab::MyDTI",
    0x20111C2C: "uPlayer::CMD_TYPE",
    0x202CBD93: "cCamRailData_0::MyDTI",
    0x20363A56: "uPlacement",
    0x20368D6C: "sShader::FUNC_LIGHTMAP",
    0x203C562B: "kCollisionSegment",
    0x20448F14: "cCamRailDataCmn_0",
    0x2046D782: "aRoom105::MyDTI",
    0x2051ABEA: "uListen::MyDTI",
    0x2063703B: "rEffectStrip::MyDTI",
    0x206E1D78: "MtGeomMinkowskiDiff",
    0x20B80399: "uEffectEdit::WORK_SET_MASS_BILLBOARD_KF",
    0x20C168FA: "rCollision::PartsInfo",
    0x20CEA95C: "uPlNeroShl000::MyDTI",
    0x20D0525D: "uDemoButton",  # pc-only
    0x20F90945: "aRoom301::MyDTI",
    0x20FB3CFD: "uPlWpRightHand::ACTION_ID",
    0x2123D97A: "MtCollada::Geometry",
    0x213257FE: "SPU_ARG_TASK_SET",
    0x21359C2A: "sCollision::Sbc",  # pc-only
    0x214022D1: "aTitle",  # pc-only
    0x21416F1C: "cEffectAnim",
    0x2145DCAA: "MOTION_PARAM",
    0x215F5B1D: "uStageSet::MyDTI",
    0x21615871: "kEmRange",
    0x2164581B: "rSoundStreamRequestXml::MyDTI",
    0x2177D537: "CellMSDSP",
    0x217FA2AB: "uStageSet00::MyDTI",
    0x218F66D1: "sCollision::Collider_0::MyDTI",
    0x21A6C6F0: "rSchedulerXml::SchedulerTrack",
    0x21B9DB92: "rSoundRandom::Header",
    0x21C47B49: "cCollisionIdx::MyDTI",
    0x21CBC535: "MtLine",
    0x21D4193A: "uEffectEdit::WORK_LIFE_FRAME",
    0x21D77EC0: "std::_String_const_iterator",
    0x21DC8364: "uAdhesion::ADHESION_OPTIMIZED_TRIANGLE_INFO",
    0x21DD1A3F: "uPlayer::kActionTbl",
    0x21F8BD4E: "sCollision::List::MyDTI",
    0x220589ED: "rEffectList::EFL_PARAM_LENS_FLARE",
    0x222A1A97: "rSchedulerXml::BoolTrack",
    0x223C9D02: "rSoundSeg::SEG_HIT_DATA",
    0x22463AC1: "cond_attr",
    0x2270E6CF: "sShader::FUNC_SHADOW_CASTER",
    0x22A93AD9: "rCameraListXml::MyDTI",
    0x22B8B4D5: "rRoomDefault::MyDTI",
    0x22BD36F5: "sResource::DecompressStream",
    0x22BE7EE5: "rCameraList::CAMERA_INFO",
    0x22CF7A0E: "sCollision::MyDTI",
    0x22E3A820: "rEffectList::EFL_HEADER",
    0x2337FF07: "uEffectEdit::WORK_SET_LIGHT",
    0x2338BD17: "uEffectVFR::TEXLINE_DATA",
    0x233F9E35: "CellGameDataSystemFileParam",
    0x23687EE1: "aRoom502::MyDTI",
    0x23693592: "uCameraCtrl::MyDTI",
    0x2374BCB8: "sShader::FUNC_LIGHTING",
    0x238E17FA: "sCollision::ColArray",  # pc-only
    0x238F4CE5: "sSoundN::SeVoice",
    0x2395ABD4: "uCapLogo::MyDTI",
    0x239E2890: "uEffectVFR::MASS_BILLBOARD_DATA",
    0x23ACB4A7: "uPowerUp",  # pc-only
    0x23CD7874: "rSoundDirectionalSetXml::Curve",  # pc-only
    0x23D73C52: "rSoundPackage::SoundSource",
    0x23F63BFF: "rSoundRandomXml::ElementData::MyDTI",
    0x2409BA4F: "std::locale::_Locimp",
    0x240CD978: "aRoom101::MyDTI",
    0x241F5DEB: "rTexture",
    0x242DB543: "rLeafAnim::Chain",  # pc-only
    0x243E399F: "rPlacementXml::ResourceTrack::MyDTI",
    0x243EA3F3: "sEffect::MyDTI",
    0x2440302E: "uCamera::MyDTI",
    0x2455007D: "uEffectEdit::WORK_MOVE_PATH_CHAIN_WORK",
    0x246BA7C1: "uAdhesion::ADHESION_TRIANGLE_NODE",
    0x247EEB9B: "rArchive::DecompressStream",
    0x248CB4C2: "uEffectEdit::WORK_SET_LINE",
    0x2491A5A0: "MtInterlock",
    0x249BC8A3: "cRotateCtrl",  # pc-only
    0x249D00B2: "rEffectSetDataList::ESL_HEADER",
    0x24B298DF: "uLightShaft::MyDTI",
    0x24B307BF: "aRoom305::MyDTI",
    0x24B76BEE: "cCnsIK::MyDTI",
    0x2507FA05: "MtFloat4x4",
    0x250D509B: "uStaffRoll",  # pc-only
    0x251523E7: "rSchedulerXml::ParamTrack::KeyBase",
    0x2515F3D3: "cTrans::PASS",
    0x251E4CC1: "sPad::PAD_VIB",
    0x254410D7: "rSchedulerXml::FloatTrack",
    0x254AA148: "_D3DVOLUME_DESC",
    0x2569B14D: "rCollision::MyDTI",
    0x257381E0: "sPathFinding::ListNode",  # pc-only
    0x25804656: "MOVE_LINE",
    0x25998008: "rSoundSourceMusicInterMediate::MyDTI",
    0x259C26D0: "kCollPrim",
    0x25A4ACBA: "uDevilCock::MyDTI",
    0x25A8998E: "cTrans::CMD_PRIMUP",
    0x25A917FE: "sCamera::VIEWPORT_NO",
    0x25ABB6A6: "rEffectStrip::INDEX_PARAM",
    0x25BC0CB2: "sRender::TempTexture::MyDTI",
    0x25CA0FB9: "cPartsHandler::cClusterParam",  # pc-only
    0x25D40B3A: "kDispTbl",
    0x25D597C1: "std::lconv",
    0x25D73B1B: "MtFile::MyDTI",
    0x25FF9B95: "uPlayer::kAtckDefTbl",
    0x26093568: "cCollisionShape",
    0x260AA208: "uDevil4Model",
    0x261E07B6: "std::_Allocator_base",
    0x262A6F84: "uStageSetSeal::MyDTI",
    0x262ADC0E: "sTool",
    0x2655CAA0: "rNavigationMeshDae::Cluster",  # pc-only
    0x26602BF5: "rSoundStreamRequest::Element",
    0x268D80DA: "rCameraListXml::CameraInfo::MyDTI",
    0x269D5CCC: "_Cmplx",
    0x26A881FA: "uEffectEdit::WORK_SET_POLYLINE_KF",
    0x26AE7963: "rCloth::Chain",
    0x26C4F741: "ANM_WORK",
    0x26DE086D: "cDefendStatus::MyDTI",
    0x26FE521D: "sprMapHead",
    0x270CDC04: "CellMSFXReverbParams",
    0x2719C951: "uSoundEngine",  # pc-only
    0x271A7B1A: "cDipData_0::DIP_ID",
    0x2722701B: "aRoom506::MyDTI",
    0x27568820: "aMission01::MyDTI",
    0x2765534B: "sLockOnTargetMgr::MyDTI",
    0x277E3026: "uEffect::WORK_CTRL",
    0x277E93B9: "sPrim::Prim::OCCLUSION_DATA",
    0x278CAE59: "rSoundPackage::MyDTI",
    0x279130C1: "aGrid::MyDTI",
    0x2799C649: "cTrans::CMD_PROFILE",
    0x27A8AFE8: "uTitle::MyDTI",
    0x27A8E510: "uPlDanteShl000::MyDTI",
    0x27C05216: "rEffectSetData::ESD_SET_RADIAL_BLUR_FILTER",
    0x27EAE89D: "rCollada",
    0x27EEC3E7: "cSystem",  # pc-only
    0x27F79ACB: "cPermitAttack",
    0x282F4C6D: "uListSelect",
    0x283F18A7: "rCollisionIdxData::MyDTI",
    0x28429AA2: "rReverb::MyDTI",
    0x2870BAD0: "uToneMapFilter::StarDef",
    0x2876811F: "aMissionTGS",
    0x2879DF0F: "rEffectSetData::ESD_MOVE_PATH_STRIP_COLL",
    0x28891C65: "uListen",  # pc-only
    0x2897356E: "cWorkRate",
    0x28A37435: "rModel::PRIMITIVE_INFO",
    0x28A831ED: "sEffectBase",
    0x28D35CF8: "uPlWpRightHand::uCollisionCtrl::MyDTI",
    0x28D5E2D9: "rSoundCurveXml::Element::MyDTI",
    0x28EC8E84: "rTexture::MyDTI",
    0x28F54A13: "uEffectVFR::MovePathChain",
    0x29090DB5: "rEffectList::EFL_PARTICLE_POLYLINE",
    0x29398EC9: "cMessageBody",
    0x293B6730: "rMotionSe::cMotionSeData::MyDTI",
    0x293EEC37: "uEffectVFR::MoveBase",
    0x29616ABE: "MtHeapAllocator::MyDTI",
    0x29A93054: "aMission01",
    0x29AD77F8: "aRoom505::MyDTI",
    0x29C7AFFF: "uLbrySelectIcon",  # pc-only
    0x29DA5AFB: "uCollTest::MyDTI",
    0x2A031018: "MtPropertyList",
    0x2A04B00F: "MtCollada::LookAt",
    0x2A083CFA: "rPlacementXml::ParamTrack",
    0x2A09CE10: "rSoundSource::MyDTI",
    0x2A1100CC: "MtFile::SEEKBASE",
    0x2A11C04E: "EFC_KEYFRAME_COLOR",
    0x2A3C005C: "aRoom306::MyDTI",
    0x2A48E123: "cCamRailDataCmn::MyDTI",
    0x2A5DFC82: "sRender::Pass",
    0x2A61075A: "sShader::MyDTI",
    0x2A65C278: "sDevil4Effect::ForceManager",  # pc-only
    0x2A74807D: "rSchedulerXml::UnitTrack",
    0x2A79940F: "uPlayer::kSPlCmd",
    0x2A83DE9B: "aRoom102::MyDTI",
    0x2A9AA103: "cActionMgr",
    0x2A9ABBA6: "cTrans::BLENDSTATE",
    0x2A9B8A46: "uKiri",  # pc-only
    0x2A9EB558: "uUnitSerializeTest",
    0x2AA68D03: "uPlayer::DMAGE_ID",
    0x2AC561A1: "cEmAppearMove",  # pc-only
    0x2ACD1930: "uColorCorrectFilter::Corrector",  # pc-only
    0x2ADF3949: "sPrim::Vertex",
    0x2B27E2F3: "MtStream_0::SEEK_ORIGIN",
    0x2B40AE8F: "rSoundEQ",  # pc-only
    0x2B711FBD: "MtAllocator::MyDTI",
    0x2B7A510F: "uToneMapFilter::MyDTI",
    0x2B810885: "MtEaseCurve",
    0x2B9ACC74: "uModel::Motion::MyDTI",
    0x2BC0CC47: "uRadialBlurFilter::MyDTI",
    0x2BC7A394: "rEffectSetData::ESD_SET_TEXLINE",
    0x2BD5E286: "uGroupData",
    0x2BDD4FE7: "uEffectEdit::WORK_SET_FILTER",
    0x2C02253A: "rEffectSetData::ESD_PARAM_COLL",
    0x2C1814B1: "cCamPanData_0::MyDTI",
    0x2C3DB165: "sLight::MyDTI",
    0x2C45F03A: "rArchive::DecompressStream::MyDTI",
    0x2C48B755: "uTgsTitle::MyDTI",
    0x2C4CEBD1: "MtObjectGroup",  # pc-only
    0x2C4DCB2A: "PS3ImportStub",
    0x2C558540: "MOT_TYPE",
    0x2C57E99D: "_Filet",
    0x2C5DD8CF: "uEm000Base::MyDTI",
    0x2C68F785: "rSchedulerXml::ParamTrack::KeyBase::MyDTI",
    0x2C7692C5: "rEffectSetData::ESD_SET_CULL_POLYLINE",
    0x2CC53994: "uEffectVFR::MassBillboard",
    0x2CE59F8B: "MtCollada::Code",
    0x2CF130AA: "MtUI",
    0x2CFF5115: "uTRResultSuji",  # pc-only
    0x2D0EE9E0: "uPlayer::RENDA_TBL",
    0x2D12C5BD: "sCollision::CALLBACK_MODE",
    0x2D12E086: "rSoundRandom",
    0x2D17DCF0: "cSpuTask::MyDTI",
    0x2D1947A5: "rModelMontage::MyDTI",
    0x2D2721E6: "uCockpitMgr",
    0x2D2A1553: "uBossCameraTest::MyDTI",
    0x2D4072DA: "rCollision::Node",
    0x2D49F0AF: "MtREDataWriter",
    0x2D54053F: "MtGeomRay_0::MyDTI",
    0x2D65CF24: "aMissionEndDemo::MyDTI",
    0x2DA6CA2C: "rFacialAnimation::FANIM_HDR",
    0x2DAD1739: "rAttributeSe::MyDTI",
    0x2DB0789C: "WEIGHT_TYPE",
    0x2DC54131: "rCloth",
    0x2DD2A208: "uModel::RenderInfo",
    0x2DD96D8E: "uPlSwordBlur",
    0x2DE77902: "aRoom501::MyDTI",
    0x2DF4BB76: "uPlayer::CHAR_ID",
    0x2DF80E18: "CellSpursJobID",
    0x2E0E8E65: "uPlayerNero::ARM_DISP_TYPE",
    0x2E10D3D8: "std::_Iterator_base",
    0x2E1BB758: "cTrans::CMD_CONDITIONAL",
    0x2E2BB8D3: "uEffectEdit::WORK_MOVE_PATH_KEYFRAME",
    0x2E30F8C4: "MtCollada::Animation",
    0x2E33501D: "sPrim::FRect",
    0x2E3FE9DB: "sSoundN::Entry",
    0x2E60C5BF: "rSoundCurveXml::Curve",  # pc-only
    0x2E6976EB: "cEnemyResetMgr::cEnemyResetCtr::MyDTI",
    0x2E759C64: "sCollision::CONTACT_MODE",
    0x2E760EA6: "aRoom302::MyDTI",
    0x2E804724: "sGpuParticle",  # pc-only
    0x2EA10CEB: "MtObject",
    0x2EA5903B: "MtCriticalSection",
    0x2EA92566: "MtProperty::Custom",
    0x2EBA9C6B: "MtCollada::Mesh::MyDTI",
    0x2ED1A340: "uScheduler",  # pc-only
    0x2ED250EF: "cSpline_0",
    0x2ED47FDC: "sCollision::TriangleInfo",
    0x2ED894B8: "rSchedulerXml::IntTrack::Key",
    0x2EDEF027: "rEventHit",
    0x2EE71EB8: "kTHINKTIMER",
    0x2EF3AAB9: "MtCollada::Scene::MyDTI",
    0x2F037DB2: "sPrim::TexCoord",
    0x2F4652A2: "rEffectSetData::ESD_SET_LIGHT",
    0x2F47A410: "uPauseSystems::MyDTI",
    0x2F61B08F: "cCamAreaConnect_0::MyDTI",
    0x2F741BF7: "uPauseMenu::MyDTI",
    0x2F753119: "MtCollada::Joints::MyDTI",
    0x2F81BB3C: "rSoundSeg::MyDTI",
    0x2F86FBB3: "uDevilCamera::MyDTI",
    0x2F8DE397: "MtGeomRay",
    0x2F97861B: "uEffectVFR::Light",
    0x2FA986EF: "aMTGSBeginDemo",
    0x2FBDB57E: "sResource::MyDTI",
    0x2FC145C0: "cSystem::MyDTI",
    0x2FCBA022: "rRenderTargetTexture::RTHEADER",
    0x2FCE9CA2: "sprMap",
    0x2FCED075: "MtCollada::Entry::MyDTI",
    0x2FE96CFA: "rSoundStreamRequest::MyDTI",
    0x2FFEE692: "sMath",
    0x300752CE: "rCameraListXml::CameraInfo",
    0x301C5975: "cCollisionShape::MyDTI",
    0x301CAB8E: "uInteractiveWater",
    0x30281234: "uWater::MyDTI",
    0x302B7B28: "uOption",
    0x302C6DA8: "uEfctJntRoute::Joint",
    0x303CEE26: "uAdhesion::ADHESION_INFO",
    0x3041B1A0: "rSndIf::cSndIfData",  # pc-only
    0x305512E9: "uCnsIK::MyDTI",
    0x3066A80D: "rShader::PARAMETER_INFO",
    0x3085CFDD: "sMediator",
    0x308AD01E: "rSchedulerXml::BoolTrack::MyDTI",
    0x308B77B8: "sRender::RENDER_STATES",
    0x308E7934: "MtGeomOBB_0::MyDTI",
    0x30C07189: "uCloth",  # pc-only
    0x30C5FA11: "MtGeomAABB",
    0x30C6E9C9: "std::malloc_managed_size",
    0x30E71356: "rEffectSetData::ESD_SET_POLYLINE",
    0x30F8D05D: "_D3DRESOURCETYPE",
    0x30FF7719: "rPlacementXml::Track::MyDTI",
    0x310B6AC9: "uEffectEdit::WORK_MOVE_PATH_CHAIN_COLL",
    0x31149351: "uYouDied::MyDTI",
    0x3116BFC8: "uLicence",  # pc-only
    0x3122CA41: "rSchedulerXml::VectorTrack",
    0x312653EA: "std::locale::facet",
    0x312EB7DD: "uFilter::PASS",
    0x313E8138: "sCollision::ContactList",
    0x31428032: "_D3DPOOL",
    0x3148A828: "uTgsDemoComing",
    0x314CC4E8: "cFrustum_0::MyDTI",
    0x315055BD: "rPlacementXml::GroupTrack",
    0x31604EE4: "uTgsComingSoon::MyDTI",
    0x317AB4ED: "rSoundSourceEnvironmentInterMediate",
    0x318B4714: "rEffectAnim::MyDTI",
    0x3192A237: "CellSpursJobList",
    0x3194A413: "uEffectVFR::Texline",
    0x3199C9B9: "cEnemyResetMgr::cEnemyResetCtr",
    0x31ACE3CA: "kCollisionIdx",
    0x31AD4835: "cArea",
    0x31DC1FF8: "rSoundPackageXml::SplitData",
    0x31F560AB: "uEffectEdit::WORK_SET_COMMON",
    0x31F693D6: "rMovieOnDisk",  # pc-only
    0x31F8026D: "sCollision::RequestPacket",
    0x31FD2B86: "rEffectList::EFL_PARAM_CHAIN",
    0x32091046: "uCnsChain::MyDTI",
    0x32195C60: "uPlayerNero::cOverDriveGuage",  # pc-only
    0x32255EB1: "uPlayerNero::kMdlHead",
    0x32334792: "uLbryBase",  # pc-only
    0x325A4D6C: "MtDataWriter::Frame",
    0x325A839F: "MtGeomConvex",  # pc-only
    0x3260C6D8: "rSchedulerXml::RefTrack::MyDTI",
    0x3261A4E2: "uGroupTable::MyDTI",
    0x3272B0A3: "rCameraXml::MyDTI",
    0x327A0394: "MtGeomRay::MyDTI",
    0x328BF1EB: "sMediator::cPlParamSave",
    0x328C0CA3: "sTool_0::MyDTI",
    0x328F5384: "MtCollada::Shader::MyDTI",
    0x32905DAB: "rPlacementXml::FloatTrack",
    0x32A86229: "aRoom508::MyDTI",
    0x32C23F37: "uPointShadowLight",
    0x32C59FC8: "uDamage::MyDTI",
    0x32D49178: "CellMSInfo",
    0x32D9FF0A: "aGrid",  # pc-only
    0x32E2B7E4: "sPhysics",
    0x32E42EB6: "uCockpit::MyDTI",
    0x32F64566: "std::_Statab",
    0x3301420E: "uUnitSerializeTestItem0",
    0x3308C90A: "EFC_PARAM_AXIS_SPD",
    0x3310A304: "ANM_HEADER",
    0x33316CDA: "cCameraRailBase",
    0x334B73F8: "uResultBack",  # pc-only
    0x335908D1: "aM01Title::MyDTI",
    0x335C32C3: "sSoundN::VOICE_STATUS",
    0x336FE45E: "uModel::MPARAM_WORK",
    0x3372827D: "MtCollada::Skin::MyDTI",
    0x338B7DAE: "uActor::LOCKONSPHERE_DAT",
    0x3395D715: "rSchedulerXml::IntTrack::MyDTI",
    0x33ABAE8D: "rClothXml::Chain::MyDTI",
    0x33BC5BA1: "uCollisionMgr",
    0x33DD067D: "cCollPrim::MyDTI",
    0x33F60CAA: "sDevil4Item",
    0x3403C103: "uEffectVFR::Billboard",
    0x342366F0: "rAttackStatusData",
    0x342487B5: "MtGeomCone",
    0x342A0C36: "sCamera::Viewport",
    0x343BEC2E: "aM00EndDemo::MyDTI",
    0x3443C8E3: "MtCollada::Element",
    0x3463BF5C: "COLLISION_ACTOR_TYPE",
    0x3498AB5F: "sDip",
    0x349D0E3E: "sPrim::Prim::METADATA_HEAD",
    0x34A705BD: "sShader::ParameterDesc::MyDTI",
    0x34A7EEC9: "rRouteNodeXml::MyDTI",
    0x34CC6276: "uGameOverSuji",  # pc-only
    0x34CE4B8A: "aInit::MyDTI",
    0x34D14DF1: "MtGeomOBB",
    0x34FE1562: "MtCollada::Library::MyDTI",
    0x35080A95: "aM00BeginDemo",
    0x351BE4BA: "MtTorus",
    0x35307C28: "uPlWeapon::ID",
    0x35618CE6: "sCollision::CONTACT_TYPE",
    0x357BFF34: "uDevilCock",
    0x358012E8: "rVibration",  # pc-only
    0x35971A64: "_CGparameter",
    0x35972AD1: "nodeLink_0",
    0x35A2DC30: "sDevil4Effect",
    0x35C7794F: "uGetItem",
    0x35DE00C1: "rRoomDefault",
    0x35F002F9: "rEffectList::EFL_KEYFRAME_FIX_ANGLE_VECTOR",
    0x36094FE3: "CellSpursJobHeader",
    0x3609565E: "cThinkMgr_0",
    0x36159E37: "rEffectSetData::ResourceInfo",
    0x3619BC32: "sStylishCount",
    0x361FB672: "uBackLight::MyDTI",
    0x363F0142: "cCnsOffset",  # pc-only
    0x36461CAE: "sCollisionGame::MyDTI",
    0x36493E32: "rEffectList::EFL_PARAM_COLL",
    0x3649EB1F: "MtColor",
    0x3651FB7E: "rSoundSystemFile::MyDTI",
    0x36531612: "EFC_ANM",
    0x36549AEE: "sGpuParticle::Particle",
    0x365B2949: "uWait::MyDTI",
    0x365B8E5B: "cEventCtrl::cRequestHandle",
    0x366A0E85: "std::_Locinfo",
    0x367CF5D7: "uViolence",  # pc-only
    0x3684D077: "uLockOnDante",  # pc-only
    0x368B0DD7: "rScheduler::MyDTI",
    0x3694A441: "rSoundCurveXml::Element",
    0x3699809F: "TASKSET_STATUS",
    0x36ACC15F: "kDefendStatus",
    0x36B25B69: "MtCollada::Skew::MyDTI",
    0x36B515FC: "uEffectVFR::MovePathStrip",
    0x36E3376B: "rEffectList::EFL_PARTICLE_DRAW_COMMON",
    0x36EAB3C8: "uUseItemBg",  # pc-only
    0x36F717CD: "FANIM_PARAM",
    0x36FDAFFB: "uLicencePc",  # pc-only
    0x370D5DC9: "rReverb",
    0x372D2D8E: "MtFloat4A",
    0x37322B5D: "FPARAM_QUATERNION",
    0x376C2228: "sCollision::NodeList::MyDTI",
    0x376EE62C: "rShader::MyDTI",
    0x377159D1: "MtFileStream::MyDTI",
    0x37821D06: "aRoom311::MyDTI",
    0x379D9806: "rModel::MyDTI",
    0x37A39C92: "uCuboidShadowLight",
    0x37A69CE3: "uStageSetBreak::MyDTI",
    0x37D110D2: "uDOFFilter::MyDTI",
    0x37F37E0E: "uPlayer::ACTION_ID",
    0x37F3C08B: "uBossCameraTest",
    0x380E5F46: "sPrim::Prim::VertexFormat",
    0x3816638E: "uModel::Constraint",
    0x382A5D5E: "sToolBase::SYSMENUINFO",
    0x3847D808: "uActorModel::EffectEmitter",
    0x384A1DCD: "MtCollada::Code::MyDTI",
    0x385FC7FE: "cUtil",
    0x3861202A: "uModel::MJOINT_WORK",
    0x386C661E: "rSchedulerXml::VectorTrack::Key",
    0x388A8A94: "cTrans::Technique::PS",
    0x388B2819: "uBackResult",
    0x389718C2: "uEffectVFR::MovePathKeyframe",
    0x38A27BE6: "MtGeometry_0",
    0x38A99B37: "rSchedulerXml::RootTrack::MyDTI",
    0x38BEE67D: "rSchedulerXml::IntTrack::Key::MyDTI",
    0x38C9D2AD: "nodeHead_0",
    0x38D04A8C: "MtCollada::Accessor::MyDTI",
    0x38F3AD96: "aM01BeginDemo::MyDTI",
    0x39082B73: "sShader::FUNC_MULTITEXTURE",
    0x39150136: "rEffectList::EFL_PARTICLE_LIGHT",
    0x39196F4D: "MtFCurve",
    0x39404C8F: "rNavigationMesh::nodeData",  # pc-only
    0x394BA276: "uMotionCamera::MyDTI",
    0x3952229F: "sys_process_param_t",
    0x3952FF47: "uCockSuji",  # pc-only
    0x395608DB: "rSoundSegXml::MyDTI",
    0x395BC87E: "JobParam",
    0x396D3A08: "rShader::TECHNIQUE_INFO",
    0x396F5422: "sDevil4Effect::MyDTI",
    0x398429E8: "cTrans::VertexDecl::VERTEX_ATTRIBUTE",
    0x39A38612: "MtCollada::BoundingBox",
    0x39A7366A: "uSysFogCtrlSt105",  # pc-only
    0x39B4DEF2: "aNative",
    0x39C13343: "rEffectList::EFL_PARTICLE_LINE",
    0x39C52040: "rCameraList",
    0x39CB9370: "rEffectSetData::ESD_MOVE_MUL",
    0x39D54997: "MtCollada::Source",
    0x39DEB851: "rPlacementXml::GroupTrack::MyDTI",
    0x39EEF98F: "std::_String_val",
    0x3A1D81D9: "MtProfiler",
    0x3A217B78: "MtCollada::Scale",
    0x3A2AFE20: "uEfctJntRoute::MyDTI",
    0x3A4BBF18: "uSpotLight::MyDTI",
    0x3A565E78: "rSchedulerXml::ResourceTrack::Key::MyDTI",
    0x3A69DED2: "CellGcmContextData",
    0x3A7CF6DD: "EFC_KEYFRAME_VECTOR",
    0x3A82790E: "cUnit",
    0x3A915393: "rArchive::MyDTI",
    0x3A962172: "rSoundDirectionalCurveXml::Element",  # pc-only
    0x3A96D8A0: "rSoundDirectionalCurveXml",  # pc-only
    0x3A97647E: "rSoundStreamRequestXml::ElementData::MyDTI",
    0x3A9B7358: "uLightScatteringFilter",  # pc-only
    0x3A9C6D41: "aRoom511::MyDTI",
    0x3A9F9545: "MtCollada::Mesh",
    0x3AC1EBAF: "uEffectEdit::UNIT_EX_CTRL",
    0x3AC5C0C9: "cCamRailData::MyDTI",
    0x3ACBC1D9: "rEffectList::EFL_MOVE_COMMON",
    0x3AF02039: "cCharTblMgr::kCtTblEnd",
    0x3AF72908: "std::string",
    0x3B02BC93: "sWorkRate::MyDTI",
    0x3B186B1A: "rSchedulerXml::Track::MyDTI",
    0x3B2F4CA5: "CellAudioPortConfig",
    0x3B4C8C80: "uGetItem::MyDTI",
    0x3B59AB6A: "uHSVFilter",
    0x3B5A0DA5: "rCollisionIdxData",
    0x3B5C1E36: "sShader::PARAM_TYPE",
    0x3B636FA6: "MtFloat4x3",
    0x3B6D00BE: "uEffectVFR::MoveCommon",
    0x3B7125A5: "rSoundCurveSetXml",
    0x3B808F1B: "uNowLoading",
    0x3B968604: "cRoomDefaultData::MyDTI",
    0x3B99A2A9: "MtEllipsoid",
    0x3BA7BF5D: "sDevil4Pad::MyDTI",
    0x3BAA9906: "rEffectList::EFL_PARAM_LINE_LENGTH",
    0x3BB59CA1: "uPlNeroShl000",
    0x3BBB734E: "MtXmlReader::WORK",
    0x3BCA0D4C: "__attribute__",
    0x3BCAFFB5: "rCameraList::MyDTI",
    0x3BD41B3A: "cCnsChain",
    0x3BF9F9AC: "uOptionSound::MyDTI",
    0x3BFDF900: "uEmTest",
    0x3C14AD49: "uTVNoiseFilter",
    0x3C26F724: "MtGeomSphere::MyDTI",
    0x3C41B241: "sResource::TypeInfo::MyDTI",
    0x3C5E64B6: "rSoundPackageXml::ProgramData::MyDTI",
    0x3C6CD320: "uPlayer::kDashParam",
    0x3C8B7CB0: "uOrb00",
    0x3CB8372A: "uHazeFilter::MyDTI",
    0x3CBAE451: "MtDebug",
    0x3CC5672B: "rMovieInterMediate::MyDTI",
    0x3CC892CC: "std::_Cvtvec",
    0x3CD3A76B: "uPowerUpBg",  # pc-only
    0x3CE9BC9A: "cEventCtrl",
    0x3D23A395: "rSoundEngine::EnginePointData",  # pc-only
    0x3D3AD05B: "CellGcmConfig",
    0x3D3DFDF1: "uEffectGenerator",
    0x3D415B1A: "cUtil::kDice",
    0x3D4CC9F7: "uDevil4Effect::MyDTI",
    0x3D568D05: "MtGeomCapsule",
    0x3D57C1B3: "std::_Locbase",
    0x3D62893E: "rGridEnvLight::SHFactor",
    0x3D698F34: "uLbryMovieTitle",  # pc-only
    0x3D7D020B: "MtCollada::Light",
    0x3D91F4B6: "cActionMgr_0::MyDTI",
    0x3D9C4B1E: "uActorModel::Constraint",
    0x3DD83E4A: "sys_memory_info",
    0x3DDC7186: "rSchedulerXml::ParamTrack",
    0x3DF84CB2: "rSoundSystemFileMSDSPTimeDomainReverb::MyDTI",
    0x3E0CB92B: "uDirectionalGlowFilter",
    0x3E1010B3: "cEventPosData",  # pc-only
    0x3E1313D4: "sys_event",
    0x3E1F7730: "sLight::BOUNDERY_TYPE",
    0x3E287173: "uPlayer::kAtckInfoBit",
    0x3E2C67E9: "rGridEnvLight::MyDTI",
    0x3E2C7923: "MtFloat3x3",
    0x3E3F1105: "uPlayer::MyDTI",
    0x3E4E9BB1: "rSoundPackageXml::MyDTI",
    0x3E55D284: "uHddInstall",  # pc-only
    0x3E7D30FB: "MtCollada::Technique::MyDTI",
    0x3EA35F43: "MtProperty::Custom::PARAM",
    0x3EA551E6: "uPlayer::DOWN_DIR",
    0x3EAB50F1: "uBackResult::MyDTI",
    0x3EB07876: "sResource::TypeInfo",
    0x3EB3AF00: "MtCollada::COLLADA::MyDTI",
    0x3ECC57A5: "MtGeometry::MyDTI",
    0x3EFCC2A9: "sprMapHead_0::MyDTI",
    0x3EFDD7E5: "cCamRailDataCmn",
    0x3F16AF36: "uPlGrabShort",
    0x3F1DDF50: "sEffect",
    0x3F2F35E2: "cEventChgRoom",
    0x3F3CE8AF: "rEffectSetData::ESD_PARAM_CHAIN",
    0x3F430898: "uPlayerNero::setGunSe::kParam",
    0x3F48EF30: "EFC_KEYFRAME_F32",
    0x3F49FAE2: "uFeedbackBlurFilter",
    0x3F5566D5: "aM00BeginDemo::MyDTI",
    0x3F6B9CEF: "uEmTest3",
    0x3F708A0D: "uLockOnCock::MyDTI",
    0x3F7474D0: "EFC_PARAM_U16",
    0x3F7F3907: "uPlWpBlueRose::MyDTI",
    0x3F8FF48A: "sPrim::Prim::LIGHT_DATA",
    0x3F9994AD: "MtXmlReader::ATTRIBUTE",
    0x3FA8F69A: "uLoadMessage",  # pc-only
    0x3FADE46C: "rEffectSetData::ESD_SET_FILTER_COMMON",
    0x3FB6126E: "aRoom308::MyDTI",
    0x3FD217B1: "aGame",
    0x3FE29203: "MtCollada::Image::MyDTI",
    0x3FEBB39F: "sResource::DecompressStream::MyDTI",
    0x3FF99995: "rSoundPackageXml",
    0x3FFA9386: "MtCollada::Combiner::MyDTI",
    0x40075618: "uSeGenerator",
    0x40150358: "cCameraNormalInitParam",
    0x40291B4F: "rReverbXml::MyDTI",
    0x402EBE7C: "rSchedulerXml::ResourceTrack::Key",
    0x403BC972: "MtGeomAABB_0::MyDTI",
    0x40500CC5: "rSoundSystemFileMSDSPTimeDomainReverbInterMediate",
    0x4055FD94: "cSplinePoints",
    0x405FA2D7: "sprMap::MyDTI",
    0x407B82BA: "uCoord::MyDTI",
    0x40820C11: "uEffectVFR::PrimModel",
    0x4084E824: "sPrim::TransInfo",
    0x408FEF9A: "sSoundN::STOP_TYPE",
    0x409EC9CA: "rRouteNode",
    0x40DCC228: "SysProcessParam",
    0x40DDFA5E: "rSoundSourceEnvironment::MyDTI",
    0x40E2E4B7: "sRender::ZcullArea",
    0x40E80DD6: "uModel::Joint",
    0x40F8EC41: "uPlayerDante::kMdlHead",
    0x40FCFFAF: "cConstraint::DIRECTION",
    0x410BBB5F: "aRoom006::MyDTI",
    0x41269586: "cCharTblMgr",  # pc-only
    0x416FF78E: "uEmTest3::Box",
    0x417917B0: "std::_Mbstatet",
    0x418C2CDD: "CellMSEnvelope",
    0x418E3772: "MtCollada::Library::TYPE",
    0x419154C9: "uBMSub",  # pc-only
    0x4194B173: "MtCollada::MyDTI",
    0x419AC448: "EFC_KEYFRAME_AXIS",
    0x41A68FC4: "uEm015::MyDTI",
    0x41B46598: "aRoom202::MyDTI",
    0x41BCC205: "std::div_t",
    0x41DCCEAF: "sCamera::REGION_MODE",
    0x41F4EC1D: "sPhysics::MyDTI",
    0x41F7F004: "rPlacementXml::ObjectTrack::MyDTI",
    0x4206B6CE: "rSoundCurveSet::Curve",
    0x420EAB57: "uEffectEdit::WORK_MOVE_PATH_KEYFRAME_COLL",
    0x4212630C: "sCollisionGame",
    0x4225123C: "aRoom401::MyDTI",
    0x422524D3: "std::_Dvals",
    0x42256225: "MtXmlReader",
    0x422DB5FC: "MtObject::MyDTI",
    0x42481BD5: "uTgsTrial",
    0x42661A7C: "uUnitSerializeTest::MyDTI",
    0x426D115F: "sEffectVFR",
    0x427C3510: "uEffectEdit::WORK_SET_HIT",
    0x4288D37F: "uPlWeapon::MyDTI",
    0x429FF316: "sCollision::List",
    0x42CF5D21: "cCamPanData",
    0x42D9F385: "rEffectList::MyDTI",
    0x42EA212F: "rPlacement",
    0x42EFB00D: "aGameOver::MyDTI",
    0x42F7B57F: "MtFile::PS3Path",
    0x430C857E: "uEffect2D",  # pc-only
    0x430CD3D1: "rCollision::MaterialList",
    0x4312C8BC: "uHemiSphereLight::MyDTI",
    0x43186DF8: "rEffectAnim::SEQ_INDEX",
    0x4333CAE8: "sDevil4Pad",
    0x4336B150: "rMotionList::MyDTI",
    0x43562668: "sRender::DISPLAY_MODE",
    0x438CBE85: "rEffectList::EFL_PARAM_LINE_FIX",
    0x4398F9BF: "MtRange",
    0x43A5CC0E: "uPlayer::kCameraAngle",
    0x43BCBC9C: "uMotionBlurFilter",  # pc-only
    0x43BDEA82: "_D3DLOCKED_BOX",
    0x43CCFADF: "uFade",
    0x43F48B85: "MtVector4",
    0x44067298: "uUnitSerializeTestItem1",
    0x4422D241: "MtRangeF",
    0x442A946D: "aMission",
    0x442D8E4F: "uMaterialHandler::MyDTI",
    0x4454F3B0: "EFC_PARAM_AXIS",
    0x445CC53B: "uInfiniteLight::MyDTI",
    0x446C2F46: "MtCollada::Camera::MyDTI",
    0x44BB75C9: "rSchedulerXml::ObjectTrack::MyDTI",
    0x44D32983: "sUnit::MoveLine",
    0x44FECED7: "EFC_KEYFRAME_COMMON",
    0x4502F4AF: "std::_Collvec",
    0x450455BD: "uEffectEdit::WORK_SET_LIGHT_KF",
    0x4506D496: "uPlayerDante::MyDTI",
    0x451816A7: "uPlayer::kParamTbl",
    0x4541B5A5: "aRoom002::MyDTI",
    0x4562CEA2: "rGridEnvLight::NATIVE_FILE_HEADER",
    0x45A468EE: "uModel",
    0x45C1D005: "uToneMapFilter::StarDef::StarLine",
    0x45C6CA28: "FACIAL_PARAM",
    0x45E3C6D3: "cCharTblMgr::kCtWait",
    0x45EC813E: "uEm011::MyDTI",
    0x45EC9B85: "uEffectVFR::LINE_LENGTH_WORK",
    0x45F1F3ED: "cAnmSprData",
    0x45FB6325: "sPrim::PrimType",
    0x45FE6B62: "aRoom206::MyDTI",
    0x46011806: "rResourceTest::MyDTI",
    0x462C5155: "std::_Uninitialized",
    0x463530B1: "aRoom::MyDTI",
    0x46389119: "rEffectSetData::ESD_SET_PRIM_COMMON",
    0x466F1CC6: "aRoom405::MyDTI",
    0x4670999A: "sCapture::TARGET",
    0x46709DDC: "nodeHead",
    0x4675DB48: "uActorModel::EffectEmitter::MyDTI",
    0x46810940: "rSoundEngineValue",  # pc-only
    0x468178E5: "DMG_STATE",
    0x469B433D: "sSpu",
    0x46A2EDAF: "sShader::VERTEX_FILTER",
    0x46AD0039: "MtBlockAllocator::MyDTI",
    0x46CA4278: "rEffectList::EFL_MOVE_ADD",
    0x46D3F463: "MtCollada::Extra::MyDTI",
    0x46DCE828: "sCollision::NodePoint",
    0x47094242: "MtRect",
    0x472B1BE1: "uInteractiveWater::MyDTI",
    0x472F737E: "nodeData::_RN_CONTACT_TYPE",
    0x473F908D: "cCollisionBase",
    0x474FE628: "MtGeomCylinder::MyDTI",
    0x4755EA45: "MtPropertyObject::MyDTI",
    0x475C3144: "uEffectEdit::WORK_SET_LENS_FLARE",
    0x47711732: "CellSpurs",
    0x477A62C6: "rPlacementXml::FloatTrack::MyDTI",
    0x477ADADA: "uCnsIK",
    0x47849B6D: "rSoundRequest::Element",
    0x47A0527A: "cTrans::Technique::MyDTI",
    0x47A53D92: "MtPropertyObject",
    0x47B6FF4F: "sException::MyDTI",
    0x47B8627F: "rSchedulerXml::ResourceTrack::MyDTI",
    0x47DE6950: "MtDataReader",
    0x47E4CA71: "MtRay",
    0x482EBEC8: "MtSerializer::PROPERTYDATA",
    0x482F8F7D: "MtCollada::Param::MyDTI",
    0x4831532E: "sPrim::Material",
    0x4837AE74: "uFacial::jointInfo",
    0x48446B5A: "EFC_PAT",
    0x4848FE71: "uNowLoading::MyDTI",
    0x484D56E6: "cTrans::TextureBase::MyDTI",
    0x48507B68: "uEmRange",
    0x4850B757: "rReverb::cReverbData::MyDTI",
    0x486D4296: "ImitationVolumeTexture",
    0x488F554D: "cThinkMgr_0::MyDTI",
    0x489D3462: "aRoom999::MyDTI",
    0x48A49044: "CellSpursJobChain",
    0x48ABC9A6: "rCameraList::CAMERA_LIST_HDR",
    0x48CFA244: "MtCollada::Material",
    0x48D35B7E: "cConstraint",
    0x48D4A626: "cCamRailDataCmn_0::MyDTI",
    0x48DBE452: "sGpuParticle::Context",
    0x48E01B25: "aRoom406::MyDTI",
    0x48E711C6: "MtColorHSV",
    0x48F16739: "MtPropertyList::Iterator",
    0x48F4A4FF: "_D3DMULTISAMPLE_TYPE",
    0x48F61C32: "cCnsTest2::MyDTI",
    0x4901B0FD: "uPlayer::kLeverParam",
    0x492BE632: "uRoom::MyDTI",
    0x49338AAA: "MtCollision",
    0x49480161: "sMessage::MyDTI",
    0x496BB11F: "cCamAreaData",
    0x498F8B2B: "uPlWpRightHand::uEffectCtrl::MyDTI",
    0x499A8BE0: "cResource::MyDTI",
    0x49A43F8E: "uPointLight",
    0x49A87E8E: "rCollision::Header",
    0x49AEB28D: "fontMap::MyDTI",
    0x49B50A44: "MtCollada::Perspective",
    0x49BC2016: "rSoundCurveSet::Element",
    0x49D36FC0: "rEffectList::EFL_MOVE_BASE",
    0x49D519C9: "rEffectList::EFL_PARTICLE_BILLBOARD",
    0x49EC4600: "sPrim::Rect",
    0x49F129D2: "uFishEyeFilter::MyDTI",
    0x4A113F1C: "EventInfo",
    0x4A1DA1F3: "sEnemyCtrl",
    0x4A2949CF: "MtString::STRING",
    0x4A3A0E90: "cCnsHand::MyDTI",
    0x4A3B6772: "cCameraPlayer",
    0x4A7368FE: "aMission::MyDTI",
    0x4A8F93CB: "z_stream_s",
    0x4A92D0E2: "cTrans::CubeTexture",
    0x4AE328B9: "MESSAGE_ATTR_INFO",
    0x4AEC04FD: "sPathFinding",  # pc-only
    0x4AEE9E5E: "uModel::MyDTI",
    0x4AF7DD87: "CellVideoOutResolution",
    0x4B0402F1: "divi4_t",
    0x4B04793E: "aDevil4::MyDTI",
    0x4B05D267: "cCameraNormal_0::MyDTI",
    0x4B207477: "CellGcmSurface",
    0x4B25768A: "uDamage::UDAMAGE_TYPE",
    0x4B27A403: "cTrans::CMD",
    0x4B30C3CB: "cSpuJob",
    0x4B378FD8: "sRender::Pass::MyDTI",
    0x4B3B9B9B: "sShader::VDECL",
    0x4B57B92F: "__TT800_State_t",
    0x4B5B71ED: "rSoundCurveSet::NATIVE_FILE_HEADER",
    0x4B5CB3B3: "MtCollada::Program::MyDTI",
    0x4B716C81: "aRoom205::MyDTI",
    0x4BA50712: "rEffectSetData::ESD_HEADER",
    0x4BCC227A: "sPrim::Material::AlphaOpType",
    0x4BCEB246: "aRoom001::MyDTI",
    0x4BE8FE5F: "cTrans::SAMPLERSTATE",
    0x4BF43E12: "MtSerializer::CLASSDATA",
    0x4C0DB839: "rScheduler",
    0x4C34EFA6: "EFC_KEYFRAME_INDEX",
    0x4C4C96BA: "sPrim::Material::AlphaType",
    0x4C54A9A0: "rSoundStreamRequest::SoundSource",
    0x4C5571B0: "aMTGSResult::MyDTI",
    0x4C5A8277: "uLight::SHFACTOR",
    0x4C62AE64: "rSoundSourceEnvironmentInterMediate::MyDTI",
    0x4C709823: "nodeData",
    0x4C88FA97: "rEffectList::EFL_PARTICLE_TEXLINE",
    0x4C9DCB3D: "uMapMgr",  # pc-only
    0x4CAA15DF: "aRoom402::MyDTI",
    0x4CC28298: "uContrastFilter",  # pc-only
    0x4CC6CDAE: "EFC_KEYFRAME_ANGLE",
    0x4CDE8F6C: "sPrim::Prim::Packet",
    0x4CEE1360: "cTrans::Texture",
    0x4CFB9FBC: "MtCollada::Param::TYPE",
    0x4D122C51: "uLockOnCock",  # pc-only
    0x4D176444: "sRouteQ::MyDTI",
    0x4D1FC268: "rSoundEngineValueXml",  # pc-only
    0x4D1FD47E: "lconv",
    0x4D336AB0: "cTrans::PARAM_DATA",
    0x4D378D94: "rSchedulerXml::FloatTrack::Key",
    0x4D3D8D4E: "uOceanWater::MyDTI",
    0x4D4CE4F2: "rClothXml::Chain",
    0x4D4D82FA: "uMotionBlurFilter::MyDTI",
    0x4D4E14AA: "uMapData",  # pc-only
    0x4D73CE8D: "MtCollada",
    0x4DA2AC5E: "MtGeomCylinder",
    0x4DA3E213: "uEnvMap::CUBIC_BLUR_VERTEX",
    0x4DA5F92B: "sShader::TechniqueDesc",
    0x4DD4481D: "sShader::FUNC_SHADOW_MASK",
    0x4DD828A1: "MtProperty",
    0x4DE76574: "uEfctBlurHandler::MyDTI",
    0x4DFFD72D: "uScriptPlayer",  # pc-only
    0x4E121795: "sPathFinding::Astar",  # pc-only
    0x4E129413: "sys_lwmutex",
    0x4E2BAF7A: "rCollision::Vertex",
    0x4E2FEF36: "rModelMontage",
    0x4E397417: "rEffectAnim",  # pc-only
    0x4E5D26A3: "MtCollisionTree::MyDTI",
    0x4E5DAD48: "cMissionEvaluate",  # pc-only
    0x4E99BC2F: "MT_MFUNC32X2",
    0x4EA59563: "uSecretClear",  # pc-only
    0x4EABD7A3: "rSchedulerXml::MyDTI",
    0x4ED63633: "uPlWpRevellion::MyDTI",
    0x4EDF18C3: "uModel::Joint::MyDTI",
    0x4F029768: "uEffectEdit::WORK_MOVE_ADD",
    0x4F0D0760: "std::_Tinfo",
    0x4F129EA3: "SPU_TASK_SET",
    0x4F3592D3: "FPARAM_VECTOR3",
    0x4F3B627B: "aRoom201::MyDTI",
    0x4F435F6B: "MtCollada::Imager::MyDTI",
    0x4F722ADC: "sGpuParticle::PacketVB",
    0x4F72B494: "cEvent::MyDTI",
    0x4F736118: "uEffectVFR",
    0x4F744E27: "uPlWpRightHand::uEffectCtrl",
    0x4F753736: "aMvgsResult",  # pc-only
    0x4F84BCBC: "aRoom005::MyDTI",
    0x4F8EA67E: "uFlowingWater::MyDTI",
    0x4FDF3281: "uEffectVFR::MoveMul",
    0x4FF0E833: "rCnsChain::MyDTI",
    0x503338ED: "__vector_signed_int",
    0x5036B6AD: "internal_state",
    0x5042EE7F: "rEventHit::MyDTI",
    0x5046A55B: "MtStream_0::MyDTI",
    0x50493662: "uSprLayout::MyDTI",
    0x504C945D: "aMissionResult::MyDTI",
    0x50621DCF: "CellSpursEventFlagClearMode",
    0x50659208: "uEffectEdit::WORK_SET_BILLBOARD_KF",
    0x50665949: "uPlWpRightHand",
    0x50747950: "aRoom208::MyDTI",
    0x507CD79D: "CellAudioOutConfiguration",
    0x507DE156: "sSoundN::SeVoice::ADSR_STATUS",
    0x50ABD7A5: "uButton",  # pc-only
    0x50AEDAC5: "cShape::WeightNode",
    0x50C53E84: "_D3DVERTEXELEMENT9",
    0x50C94337: "uFlatWater::MyDTI",
    0x50D0B81C: "uEffectEdit::WORK_SET_TEXLINE",
    0x50DEC095: "cCharTblMgr::kCtContactClr",
    0x50F9DB3E: "rShader",
    0x510569E8: "uEm010CrawShl::MyDTI",
    0x510C1959: "uDevil4Fog",  # pc-only
    0x511910C9: "cRoomDefaultPlayer",  # pc-only
    0x51359E10: "CellSpursTaskset",
    0x513D8060: "rClothXml",
    0x514DDFB7: "sArea",
    0x517A3504: "rEffectList::ResourceInfo",
    0x518763AF: "sStylishCount::COMBO_RANK",
    0x51B1959D: "uCamera",
    0x51B91986: "rMovie::VideoDesc",
    0x51BF8A5F: "rCameraXml",
    0x51D664E8: "MtCollada::Rotate",
    0x5204D557: "rShape",
    0x522E1E7E: "rSoundRequest::MyDTI",
    0x522F7A3D: "rFacialPattern",
    0x5247ED6A: "uActor::ACTOR_TYPE",
    0x5255F31F: "uPlacement::MyDTI",
    0x526C1DBE: "uSpotShadowLight::MyDTI",
    0x52857F21: "aRoom216::MyDTI",
    0x528DC8A5: "kAttackStatus",
    0x5297957D: "uEm001::MyDTI",
    0x52A39F40: "sDevil4Sound::DEVIL4_SE_SEARCH_KEY",
    0x52A6BB53: "uCinemaScope::MyDTI",
    0x52AACCAB: "rPlacementXml::ObjectTrack",
    0x52B500AE: "cTrans::DRAWSTATE",
    0x52C13D32: "cCameraBase",
    0x52C72BC9: "std::_String_base",
    0x52D40310: "rSoundEQ::cEQData",  # pc-only
    0x52D76857: "uSeGenerator::SeGeneratorRequestWork",
    0x52D7E22D: "uGroupData::MyDTI",
    0x52EDE024: "sEnemyCtrl::MyDTI",
    0x52F9BE39: "cPartsHandler",  # pc-only
    0x530F99F7: "uLbrySuji",  # pc-only
    0x53163843: "cSprAnm",
    0x531663A4: "aTitle::MyDTI",
    0x532ED804: "MtCollada::Vertices::MyDTI",
    0x5347C170: "sRender::TileArea",
    0x53704FEC: "rSoundPackage::Header",
    0x53783AD4: "MtGeometry",
    0x537A911E: "uFilter::BLEND_TYPE",
    0x537E3563: "uEffectVFR::MyDTI",
    0x538120DE: "rSoundEngine",  # pc-only
    0x53A6DCBA: "sStylishCount::MyDTI",
    0x53B91105: "uEffectVFR::POLYGON_DATA",
    0x53BDFCE0: "EFC_PARAM_U8_DUAL",
    0x53D12C99: "uEffectVFR::LifeFrame",
    0x53E0B45E: "MtRsxHeapAllocator::HEAP_INFO",
    0x53F155D9: "sBenchmark::BenchmarkInfo",  # pc-only
    0x53F5C180: "MtSphere",
    0x53FF0F5F: "uEffectEdit::WORK_SET_POLYLINE",
    0x5404C39B: "uEfctPlGrab",
    0x540B23D9: "uMStartSuji",  # pc-only
    0x540C0687: "uCapLogo",  # pc-only
    0x541A3AAC: "uTgsGameOver",
    0x5421B7C6: "uEffectEdit::WORK_SET_TEXLINE_KF",
    0x542434FC: "rCloth::Constraint",
    0x543B5006: "uPlayer::kJumpParam",
    0x54488B12: "uEm021",
    0x54498FD1: "sLockOnTargetMgr",
    0x5475514E: "rPlacementXml::RootTrack::MyDTI",
    0x5481A96D: "aRoom008::MyDTI",
    0x54830E66: "MtCollada::Library",
    0x5487FEBA: "uImagePlaneFilter::MyDTI",
    0x549847FC: "uTVNoiseFilter::trans::SCREEN_VERTEX",
    0x54A47FFE: "uBackLight",
    0x54AA1EAC: "rSchedulerXml::VectorTrack::Key::MyDTI",
    0x54C804A0: "MtCollada::Asset",
    0x54DDDFA8: "sCapture::MyDTI",
    0x54E8E39D: "rClothXml::Index_0::MyDTI",
    0x5540F121: "uUnitSerializeTestItem1::MyDTI",
    0x554489D1: "MtXmlReader::PARSE_STATE",
    0x554ECA13: "cMessDraw",
    0x556273E7: "cMessageHead",
    0x556CB947: "aMissionSelect",  # pc-only
    0x5579F528: "rEffectSetData::ESD_SET_PRIM_MODEL",
    0x5598DE5B: "uEffectEdit::WORK_SET_POLYGON_KF",
    0x559AB9C1: "MtFCurve::Key_0::MyDTI",
    0x559F244C: "MtFile::FileInfo",  # pc-only
    0x55B9C6D9: "aMTGSResult",
    0x55D481F3: "uPlayer::kLegIkParam",
    0x5613398D: "sSoundN::DSPUnit",  # pc-only
    0x5613DD5D: "uPlayer::cWeaponCtrl",  # pc-only
    0x5614BCA1: "uCameraCtrl",
    0x56384024: "std::_Lockit",
    0x56444CCE: "uActor",
    0x564C1A79: "uTutorialGame",  # pc-only
    0x565C3FFE: "rSoundStreamRequest::Atrac3PlusManager",
    0x566A8686: "codetype",
    0x5682C5C9: "MtStream::MyDTI",
    0x56A76488: "MtStream_0",
    0x56B49B42: "CellSpursJobGuard",
    0x56B77735: "MtCollada::BoundingBox::MyDTI",
    0x56CF71DB: "aRoom212::MyDTI",
    0x56F5B156: "uModel::Motion",
    0x571BD69E: "cCnsOffset::MyDTI",
    0x57270A19: "rEffectSetData::MyDTI",
    0x572FF2B1: "nodeLink",
    0x573999C7: "cCamPanData::MyDTI",
    0x574F00FD: "rSoundSourceMusic::MyDTI",
    0x5750C1E3: "uEffectEdit::WORK_MOVE_PATH_KEYFRAME_WORK",
    0x577371AC: "cDbgPlayer",
    0x57769AB0: "uToneMapFilter::STAR_TYPE",
    0x57895BBC: "uEffectVFR::Line",
    0x57994D6D: "MtCollada::Instance::MyDTI",
    0x57A27C8C: "uPlayerNero::setGunEffect::kParam",
    0x57B77761: "uToneCurveFilter",
    0x57CD5FA3: "uModelShape::MyDTI",
    0x57D178A2: "sprMap_0::MyDTI",
    0x57EA0D1A: "MPARAM_QUATERNION3",
    0x57FA189D: "MtCollada::Channel",
    0x58407638: "aRoom211::MyDTI",
    0x589F3601: "rEffectSetData::ESD_SET_CHAIN_POLYLINE",
    0x58A15856: "rModel",
    0x58C72E3D: "sApp::Item",  # pc-only
    0x58CCDE43: "sSoundN::PAUSE_TYPE",
    0x58CD014D: "uModel::Constraint::MyDTI",
    0x58D1AFE4: "cCollGroup::MyDTI",
    0x58DF8E2B: "uPlayerNero::MyDTI",
    0x58E09A7E: "MtSerializer::MODE",
    0x58F1D822: "cTrans::VertexBuffer",
    0x59072CB9: "cCamAreaData_0::MyDTI",
    0x59176DA3: "uEffectEdit::KF_INDEX_TBL",
    0x592D804B: "rSoundCurveXml",
    0x5933A33A: "rMotionSeXml",
    0x597CDBB7: "rShapeWeight::WEIGHT_HDR",
    0x5982031D: "uInfiniteLight",
    0x59829E33: "uCockpitMgr::MyDTI",
    0x5989C70D: "MtCollada::Skin",
    0x59AF4EDF: "rSchedulerXml::SystemTrack::MyDTI",
    0x59BCC737: "uOptionSound",
    0x59C322FF: "cCnsRandom::MyDTI",
    0x59C481CF: "uPlayer::cBenchmarkCtrl",  # pc-only
    0x59E4F6E4: "uEffectEdit::WORK_SET_MASS_BILLBOARD",
    0x59F8758E: "MtMath",
    0x5A24B64C: "MtCollada::Geometry::MyDTI",
    0x5A25F18A: "rEffectList::EFL_PARTICLE_PRIM_MODEL",
    0x5A2BB2FF: "cEventHitData::MyDTI",
    0x5A4175DC: "uPlayer::PARAM_ID",
    0x5A584086: "cCamDataHeader_0",
    0x5A62EE8C: "sUnit",
    0x5A8DC249: "aInit",
    0x5A962B19: "uTgsComingSoon",
    0x5AA39A15: "uEm018::MyDTI",
    0x5AC138F3: "uEffectEdit::WORK_SET_MODEL_COMMON",
    0x5AC9CB70: "rSoundEQXml",  # pc-only
    0x5ACA61AB: "aM01BeginDemo",
    0x5AD152AF: "aM00EndDemo",
    0x5AE10A29: "cCameraRailBase::MyDTI",
    0x5AF0348C: "MtDefaultAllocator",
    0x5AF4E4FE: "rMotion",
    0x5B07854C: "rPlacementXml::MyDTI",
    0x5B0F079D: "MtRsxHeapAllocator::MyDTI",
    0x5B115DEB: "cDbgBase",
    0x5B13B7B0: "cTrans::TextureBase",
    0x5B3A2A19: "MtGeomPlane",
    0x5B466EDF: "uAdhesion::FUNC_ADHESION_ALPHA_TYPE",
    0x5B558785: "cSpline",
    0x5B87D150: "nodeData_0",
    0x5B9071CF: "rCollisionShape",
    0x5BA7E7A9: "MtDTI",
    0x5BADC52F: "MtCollada::Accessor",
    0x5BB2469D: "uTitlePc",  # pc-only
    0x5BC443CD: "MtMemoryStream",
    0x5BDD7F3B: "uCloth::Chain",
    0x5BEB8248: "nodeLink_0::MyDTI",
    0x5BF041FB: "uBPResultBack",  # pc-only
    0x5C09B966: "uModelStencil::MyDTI",
    0x5C0A78C2: "aRoom215::MyDTI",
    0x5C0F0391: "MtClipboardStream::MODE",
    0x5C1E5AC9: "rSchedulerXml::ParamTrack::MyDTI",
    0x5C2D5CEA: "cTrans::CONTEXT",
    0x5C2D6B01: "uEffectVFR::CHAIN_WORK",
    0x5C3B1F23: "sEffectBase::MyDTI",
    0x5C4B4596: "MtCollada::Input::MyDTI",
    0x5C4D7A1A: "MtFCurve::Key",
    0x5C561A67: "rPlacementXml::BoolTrack::MyDTI",
    0x5C6E6078: "sMessage",
    0x5C73C892: "uNoiseFogFilter::MyDTI",
    0x5C827B98: "sCamera::MyDTI",
    0x5C9F2B5D: "nodeData_0::MyDTI",
    0x5CB51EA6: "kVectorCurve",
    0x5CB6D076: "uPlayer::kActionData",
    0x5CB82BA4: "rResourceTest",
    0x5CB86417: "MtOBB",
    0x5CBAB342: "rSoundSourceEnvironment",
    0x5CC94315: "rTexture::HEADER",
    0x5CCDEA6A: "uEffect",
    0x5CD23807: "MtXmlReader::ENCODE_TYPE",
    0x5CDD1F19: "cResource",
    0x5CEBA127: "uPlayer::kPadInfo",
    0x5CEFBD8C: "SysPrxParam",
    0x5CFCE845: "uEffect::MyDTI",
    0x5CFF2DA1: "uSave",  # pc-only
    0x5D172650: "aRoom997::MyDTI",
    0x5D25820D: "cWorkRate::MyDTI",
    0x5D2E6F95: "MtCylinder",
    0x5D35B672: "aGameOver::STATUS",
    0x5D3949F9: "rCollision::Edge",
    0x5D3CA400: "ImitationCubeTexture",
    0x5D43D8E1: "MtCollada::Camera",
    0x5D46A735: "uMaterialHandler",
    0x5D4C4B65: "std::_String_iterator",
    0x5D6A0917: "aRoom408::MyDTI",
    0x5D757558: "cEventHitData_0",
    0x5D76ACED: "CellVideoOutConfiguration",
    0x5D87A41B: "EM018_FIRE",
    0x5D8C1B95: "rEffectList::EFL_PARTICLE_HIT",
    0x5D96EED9: "sCollision::Collider_0",
    0x5D97DF7B: "uEm031::cCmnd",  # pc-only
    0x5D98B4F2: "cShape::transBlend::MAP_VERTEX",
    0x5DD3D1F2: "uPlWpEbonyIvory::MyDTI",
    0x5DDB44F8: "rSoundSystemFileMSDSPTimeDomainReverb",
    0x5DF350C7: "uPlGrabShort::MyDTI",
    0x5DF5EC93: "cTrans::IndexBuffer::MyDTI",
    0x5DF87B9C: "cFrustum_0",
    0x5E04E488: "EFC_SEQ",
    0x5E0DD5E0: "kCollisionBox",
    0x5E0E24B4: "cDipData::MyDTI",
    0x5E7235D8: "rSoundSeg::LayoutInfo::MyDTI",
    0x5E8DD4F8: "nodeHead::MyDTI",
    0x5E8F4756: "MtCollada::Node",
    0x5E9A2C4A: "aMissionTitle",  # pc-only
    0x5EA5C4B9: "sCapture::FORMAT",
    0x5EAE00C2: "aMission00",
    0x5EDCCF2B: "uCockpitSub",  # pc-only
    0x5EE442E1: "sStylishCount::ATTACK_RANK_REGULATION_VALUE",
    0x5F109FE8: "cMotionCtrl",  # pc-only
    0x5F1D005A: "MtGeomMinkowskiDiff::MyDTI",
    0x5F3089C1: "sPrim::MyDTI",
    0x5F3A8EBB: "rNavigationMesh::nodeInfo",  # pc-only
    0x5F48DA11: "uEffectGenerator::UNIT_SET_CTRL",
    0x5F4FA3AC: "sFile::MyDTI",
    0x5F51A7DD: "rSoundRequestXml::MyDTI",
    0x5F532308: "cCnsDirPos",
    0x5F5B81AE: "CHAR_ATTR_INFO",
    0x5F68C17A: "uGridEnvLight::MyDTI",
    0x5F75400F: "rAttributeSeXml",
    0x5F813CB8: "MtAllocator",
    0x5F835B50: "cFrustum",
    0x5F84F7C4: "rMovieOnMemory",  # pc-only
    0x5F9890E3: "uOceanWater::WATER_VERTEX",
    0x5FAC3BB5: "EM000BASE_DIE_TYPE",
    0x5FB5EB39: "cCharTblMgr::kContactData",
    0x5FEE0946: "sMain::JOB_WORK",
    0x5FF27EBD: "cBranchScript",  # pc-only
    0x60524FBB: "rShapeWeight",
    0x6057874C: "uListSelect::MyDTI",
    0x60711D85: "rSoundSourceSEInterMediate::MyDTI",
    0x6072BA70: "uPlayerDante::setGunEffect::kParam",
    0x607A61CD: "cCharTblMgr::kCtContact",
    0x60842DCC: "rClothXml::Constraint",
    0x608EA92F: "cSplinePoints::MyDTI",
    0x60B1426F: "rEffectList::EFL_PARTICLE_COMMON",
    0x60C10879: "uHemiSphereLight",
    0x60E99FAB: "cSpuJob::MyDTI",
    0x60FD980E: "sStylishCount::REPETITION_STATUS",
    0x612FECD2: "sCollisionGame::CHECK_GROUP_MODE",
    0x613B2AB2: "rEffectSetDataList",
    0x6143BD7B: "uEffectVFR::Particle",
    0x6144E799: "uEffectVFR::BILLBOARD_DATA",
    0x614D799C: "aRoom500::MyDTI",
    0x614DE54C: "rSchedulerXml::RefTrack",
    0x614FAFB8: "cCameraNormal::MyDTI",
    0x6167A960: "sCapture::ANTIALIASING",
    0x61693DEB: "uEnemySetCtrl::MyDTI",
    0x616F7A89: "rSoundRandom::Element",
    0x616FD810: "rSchedulerXml::RootTrack",
    0x61778A08: "MtFloat2A",
    0x617FB797: "MtCollada::Channel::MyDTI",
    0x619069AB: "uOptionScreen::MyDTI",
    0x61EA55B9: "sPad::PAD_REPEAT",
    0x61F30B0D: "sprMapHead_0",
    0x62358F2A: "sMediator::cMousePointerCtrl",  # pc-only
    0x623B054E: "cCamRailData",
    0x626EAD80: "uTVNoiseFilter::MyDTI",
    0x626F850C: "uOption::MyDTI",
    0x6281C5D2: "uPlWeapon::kConstOfs2",
    0x628E9D54: "cTrans::MATERIAL",
    0x629D7207: "uColorSpaceFilter",
    0x62A7210C: "rSoundSourceVAG::FILE_HEADER",
    0x62DC0E38: "aRoom303::MyDTI",
    0x62E212D7: "rSoundSystemFileMSSPURS::MyDTI",
    0x62E52C90: "sSoundN::Voice",
    0x62FB0FF8: "cTrans::ArrayTexture",  # pc-only
    0x6322B585: "MtCollada::Matrix::MyDTI",
    0x63234107: "uEffectVFR::LINE_DATA",
    0x632751D6: "uPlayer::kMotLoadParam",
    0x632AF747: "cActionMgr::MyDTI",
    0x6333899F: "cRoomDefaultData",
    0x633F6BBB: "uTitleA",  # pc-only
    0x6343BB79: "sMain::JOB_WORK32",
    0x635882DE: "uLbryModelTitle",  # pc-only
    0x6375C70C: "uPlayer::kActStatBit",
    0x637C2423: "sPad::PAD_INFO",
    0x63917AB7: "CellFsAio",
    0x639BDEC0: "uPlayer::CMD_ID",
    0x63A491A4: "sMath::MyDTI",
    0x63A89930: "MtCollada::Joints",
    0x63C1DD0B: "uDevilCamera::ENUM_VIB2_TYPE",
    0x63E0B536: "rEffectList::EFL_PARTICLE_FILTER_COMMON",
    0x63E298A0: "MtCollada::Pass::MyDTI",
    0x63EA4AD4: "MtCollisionTree::Node::MyDTI",
    0x64087B34: "sPrim::Prim",
    0x640E20C1: "uCnsChain",
    0x641DBAC4: "MtHeapAllocator::HEAP_INFO",
    0x644E389B: "uEffectGenerator::MyDTI",
    0x6454C1B1: "uPlayer::kPoseParam",
    0x6463ECE9: "cAttackStatus::MyDTI",
    0x646EA006: "uBossCock::MyDTI",
    0x647FB6CF: "uFeedbackBlurFilter::MyDTI",
    0x6487CDCE: "uCollisionMgr::MyDTI",
    0x64A84806: "MtFile::FileInfo::MyDTI",
    0x64BE6436: "rShape::MyDTI",
    0x64D81F88: "uPlayer::kDamageParam",
    0x64E507E3: "uDevilCamera",
    0x64EA1111: "uScreenMap",
    0x64EFBB3D: "aMTGSEndDemo",
    0x64FA433E: "uEnemySetCode",
    0x6503EBDC: "CellSpursEventFlagDirection",
    0x65049535: "uCrossFadeFilter::MyDTI",
    0x65077766: "aRoom504::MyDTI",
    0x650CA73C: "CellGameDataCBResult",
    0x6514C5D5: "uResultFigure::MyDTI",
    0x652B183C: "uSkillListMgr",  # pc-only
    0x6543BA02: "rEffectList::EFL_MOVE_PATH_COMMON",
    0x6548E193: "sDevil4Item::MyDTI",
    0x655E3E0F: "uModelGlass::Freeze",
    0x6562CE18: "rMotionSe::cMotionSeData",
    0x6588661C: "MtMemoryStream::MODE",
    0x658CDD50: "uSchedulerEdit::MyDTI",
    0x65A92F7F: "fontMap",
    0x65AFBBEF: "uPlWeapon",
    0x65B870F8: "rDevilCamera::MyDTI",
    0x65C95D39: "std::locale",
    0x65CBD139: "uTgsTitleWhite::MyDTI",
    0x65DBD4BC: "sPad::PAD_FREE",
    0x65F2CC26: "rEffectSetData::ESD_SET_MASS_BILLBOARD",
    0x660C5216: "uPlayer::kEfctCtrl",
    0x660F1F15: "std::nothrow_t",
    0x6623E378: "uSe::MyDTI",
    0x66299460: "rSndIf",  # pc-only
    0x6629DE05: "aRoom103::MyDTI",
    0x662CB6B5: "sDevil4Sound",
    0x6634250E: "rSoundRequestXml::ElementData::MyDTI",
    0x6639183B: "MtCollada::Primitive::MyDTI",
    0x66421165: "uPlayer::JUMP_INIT_TYPE",
    0x665BC6EF: "sCollision::NodeList",
    0x66948317: "MtCollada::Handler",
    0x669600C2: "aRoom307::MyDTI",
    0x66F366EF: "cEventScript",
    0x66F9F62F: "MtProfiler::Profile",
    0x67007A92: "cResource::XmlHandler",
    0x6731F9C2: "cCameraRect3D::MyDTI",
    0x673A0EFF: "rSoundSourceVAG::MyDTI",
    0x674F8683: "rRouteNodeXml",
    0x6750DF76: "rSoundSource::Descriptor",
    0x6752005F: "uCrossFadeFilter",  # pc-only
    0x675B50C3: "sToolBase::MyDTI",
    0x675C383A: "uEffectEdit::WORK_MOVE_MUL_COLL_KF",
    0x6770F33C: "rEffectList::EFL_KEYFRAME_COLOR",
    0x677BD269: "uFlatWater",
    0x677EF8EB: "uCnsOffset::MyDTI",
    0x67939C72: "uAttributeSe::MyDTI",
    0x67BA50D2: "MtPoint",
    0x67C10259: "cTrans::CMD_IPRIM",
    0x67DD6673: "aMissionBeginDemo::MyDTI",
    0x67E3773B: "cTrans::CMD_PRIMCALL",
    0x67E87A51: "cCnsDirPos::MyDTI",
    0x67EEE15E: "MtCollada::Program",
    0x67F20F40: "cTrans::TAG",
    0x6816B494: "MtFCurve::MyDTI",
    0x68190721: "aRoom304::MyDTI",
    0x682C6576: "aDevil4Grid::MyDTI",
    0x683F528C: "rPlacementXml::RefTrack::MyDTI",
    0x687F845B: "ANM_SPRITE",
    0x6882EC32: "sShader::FUNC_NORMALMAP",
    0x6886231B: "rPlacementXml::VectorTrack",
    0x68942296: "CellVideoOutState",
    0x68A6D9E6: "aRoom100::MyDTI",
    0x68B53965: "rPlacementXml::UnitTrack::MyDTI",
    0x68BD663D: "cDbgSoftDip",
    0x68CAEB51: "MtGeomLine",
    0x68EA6552: "rPlacementXml::ResourceTrack",
    0x68FEB200: "uEm011CrawShl::MyDTI",
    0x69020EED: "uWater",
    0x69417260: "cStageSetFlagMgr::cRoomSetFlag",  # pc-only
    0x6954FA33: "MtGeomMinkowskiSum",
    0x696DA2AC: "std::_Iosb",
    0x69721F6F: "MtCollada::Translate",
    0x699CA091: "rEffectSetDataList::ESD_INDEX",
    0x69A34A33: "rAttributeSe::cAttributeSeData::MyDTI",
    0x69A7116B: "rSoundSystemFileMSSPU::MyDTI",
    0x69AE409E: "uEnemy",
    0x69B05BA5: "rSndIfXml",  # pc-only
    0x69BEFE4A: "sEffectBase::FilterControl",
    0x69C2228D: "uCloth::Chain::MyDTI",
    0x69CA4341: "rPlacementXml::IntTrack::MyDTI",
    0x69D19853: "inflate_state",
    0x69D8BA6B: "uPlayer::MOT_CANCEL",
    0x69DA81A5: "lwmutex_attr",
    0x6A000349: "rEffectSetData",
    0x6A2B8798: "rAttributeSe::cAttributeSeData",
    0x6A414C06: "uModel::Constraint_0",
    0x6A48215A: "rSoundRandomXml::ElementData",
    0x6A85AFB6: "rEffectList::EFL_MOVE_PATH_STRIP",
    0x6A85D64E: "sShader::FUNC_SKIN",
    0x6AAE5D4C: "sGpuParticle::PROCESSING_MODE",
    0x6AB61A89: "uOceanWater",
    0x6AE27F28: "uMotionCamera",
    0x6AF6B71F: "cDbgSystemSetting",
    0x6AF98BDE: "MPARAM_HERMITE3",
    0x6AFE872C: "cCamAreaConnect",
    0x6B0373F6: "rSoundCurveSet::List",
    0x6B06C0D7: "cTrans::CMD_CLEAR",
    0x6B1C7A35: "cCnsMatrix::MyDTI",
    0x6B38CFE6: "cTrans::MyDTI",
    0x6B39DD47: "uDemoSpr",  # pc-only
    0x6B4949DF: "uEffectEdit::WORK_MOVE_NONE",
    0x6B4EA458: "uToneMapFilter::GLARE_TYPE",
    0x6B53FECB: "uModelGlass::MyDTI",
    0x6B5554A6: "uEffectVFR::Culling",
    0x6B72EB09: "MtFloat3",
    0x6B86B648: "uStaffRollCnt",  # pc-only
    0x6B887085: "aRoom507::MyDTI",
    0x6B8A7A97: "rSchedulerXml::RefTrack::Key::MyDTI",
    0x6B957D14: "std::locale::id",
    0x6BAF30A7: "cCollisionIdx",
    0x6BB2D593: "uMessage::MyDTI",
    0x6BBD13B7: "rClothXml::MyDTI",
    0x6BC55274: "uEffectEdit::WORK_MOVE_PATH_STRIP",
    0x6BCE241C: "rEffectList::EFL_MOVE_PATH_KEYFRAME",
    0x6BDD7E0D: "rEffectAnim::SEQ_PAT",
    0x6BE70866: "aDevil4",  # pc-only
    0x6BFC88BE: "aMission00::MyDTI",
    0x6C050C3A: "rSoundSourceAT3::MyDTI",
    0x6C078EAB: "uVolumeNoiseFilter::MyDTI",
    0x6C1CCE18: "sPrim::Prim::Tag",
    0x6C25268B: "uPlShlTest::MyDTI",
    0x6C31AB0E: "uNowLoadingTex",  # pc-only
    0x6C5309DB: "aRoom300::MyDTI",
    0x6C619332: "MtMemory",
    0x6C670AEB: "uEffectEdit::WORK_MOVE_MUL_COLL",
    0x6C710A08: "uDemoCutCtrl",  # pc-only
    0x6C84270F: "rEffectList::EFL_KEYFRAME_F32",
    0x6CAAC5D2: "uPlayer::CMD_CHECKSUB",
    0x6CAF1232: "cDefendStatus",
    0x6CC76A1B: "rSoundDirectionalCurveXml::Curve",  # pc-only
    0x6CD749D1: "rEffectStrip::PARTS_PARAM",
    0x6CDACB44: "aMissionEndDemo",
    0x6CECD71C: "aRoom104::MyDTI",
    0x6CF72E4E: "sPad::MyDTI",
    0x6CF860D2: "rSoundSystemFileMSSPU",
    0x6D0C7FDD: "MT_MFUNC32",
    0x6D2708BA: "uEffectEdit::WORK_SET_PRIM_MODEL_KF",
    0x6D2DC109: "uEnemy::MyDTI",
    0x6D3247B1: "cEventCtrl::MyDTI",
    0x6D3557F7: "MtXmlWriter::SCOPE",
    0x6D4DF368: "std::fpos_t",
    0x6D6BE970: "uPlayer::kPadAnlg",
    0x6D70724D: "std::_Container_base",
    0x6D8FFC44: "cTrans::VSTREAM",
    0x6D90EA75: "rSoundSystemFileMSSPUInterMediate::MyDTI",
    0x6D9CD5C2: "uEffectEdit::WORK_LIFE_KEYFRAME",
    0x6DBD21EC: "rMovie::MyDTI",
    0x6DD3C136: "rEffectSetData::ESD_MOVE_ADD",
    0x6DE535EB: "uPlWpRightHand::uCollisionCtrl",
    0x6DF54A3A: "rArchive::ARCHIVE_HDR",
    0x6E0A7787: "rSoundCurveXml::MyDTI",
    0x6E239774: "uPlayer::JUMP_TYPE",
    0x6E45B89A: "uPlSwordBlur::MyDTI",
    0x6E4BFD2F: "MtGeomCone::MyDTI",
    0x6E4CB122: "cTrans::CMD_RT",
    0x6E4F7088: "cEnemyCreateData",
    0x6E57778C: "MESS_QUEUE_DATA",
    0x6E60F7B4: "uActorModel::MyDTI",
    0x6E6158C1: "MtCollada::Primitive::TYPE",
    0x6E61B3FC: "_D3DVIEWPORT9",
    0x6E795483: "SEQUENCE_INFO",
    0x6E90399D: "rEffectList::EFL_PARTICLE_MASS_BILLBOARD",
    0x6E9F47C9: "cTrans::VertexDecl",
    0x6EC8CDF5: "sRouteQ",
    0x6ECF7794: "rSchedulerXml::FloatTrack::MyDTI",
    0x6ECFD154: "aM00Title::MyDTI",
    0x6ED02D12: "cTrans::Technique::VS",
    0x6EEE585B: "rSchedulerXml::BoolTrack::Key::MyDTI",
    0x6F0B3C5A: "uPowerUpMgr",  # pc-only
    0x6F0DAA0B: "rEffectSetData::ESD_MOVE_ADD_COLL",
    0x6F16D3CF: "cTrans::Technique::SHADERPARAM",
    0x6F3BF2D1: "MtHalf4",
    0x6F4CA06B: "cCamDataHeader::MyDTI",
    0x6F4F1117: "uColorSpaceFilter::MyDTI",
    0x6F5589AE: "sSoundN::SeEntry",
    0x6F5A9CCD: "uMovie::STATUS",
    0x6F6F6347: "MtCollada::LookAt::MyDTI",
    0x6F861650: "MtFile::TIME",
    0x6F915012: "uModeClear",  # pc-only
    0x6F9DABEE: "rGridEnvLight",
    0x6FACAECE: "rEffectList::EFL_PARTICLE_POLYGON",
    0x6FBB5E31: "uEmSample",
    0x6FBB7FED: "_LARGE_INTEGER",
    0x6FC27E7F: "aRoom503::MyDTI",
    0x6FC48424: "rEffectSetData::ESD_EXT_LENS_FLARE",
    0x6FCCAE43: "MtCollada::Rotate::MyDTI",
    0x6FE26273: "uClothSim1D",
    0x70016EE5: "sUnit::MyDTI",
    0x7019A20C: "_D3DRENDERSTATETYPE",
    0x7019A5CF: "sDevil4Sound::MyDTI",
    0x701D5D68: "sResource",
    0x70282481: "cTrans::CMD_RS",
    0x7044A39F: "MtCollada::Controller::MyDTI",
    0x704F4415: "rEffectSetData::ESD_SET_BILLBOARD",
    0x704FE852: "uToneMapFilter",
    0x706444EB: "MtCollada::Texture::MyDTI",
    0x707BD727: "sShader::ParameterDesc",
    0x709137C4: "cCameraNormalInitParam_0",
    0x7098BA40: "rSoundEngineValue::cValueData",  # pc-only
    0x709B7037: "uPlayer::ATCK_RANGE",
    0x709E4C4C: "MtCollada::Light::TYPE",
    0x70A0F6B7: "sPathFinding::ListControl",  # pc-only
    0x70B3DA89: "rMessage::MyDTI",
    0x70C56D75: "MtGeomAABB::MyDTI",
    0x70CC7783: "uHazeFilter",
    0x70DB4A29: "rSprLayout::MyDTI",
    0x70F9C214: "uGameOver::MyDTI",
    0x7101CACB: "cCameraNormalInitParam::MyDTI",
    0x7102B683: "sSoundN::VOICE_COMMAND",
    0x710AFEBB: "rShape::SHAPE_TARGET",
    0x71134D41: "MtArray",
    0x711AF113: "aAdvertise",  # pc-only
    0x711C945D: "cCamAreaData::MyDTI",
    0x71304BAA: "cTrans::Texture::MyDTI",
    0x71329731: "rShapeWeight::MyDTI",
    0x71455E09: "CellPadData",
    0x7147B818: "MtCollada::Imager",
    0x714AD3C8: "std::_Timevec",
    0x7168D3F4: "rSchedulerXml::ResourceTrack",
    0x717ACD49: "uSecretFailed",  # pc-only
    0x71950384: "rMovieOnDiskInterMediate",  # pc-only
    0x71A8FCE7: "uEmTest::MyDTI",
    0x71AF5729: "cCamDataHeader_0::MyDTI",
    0x71BE1473: "OPDEntry",
    0x71BE50E3: "uEm019",
    0x71DDC0F1: "sRender::TempTexture",
    0x72073296: "sDevil4Debug",
    0x725E42BA: "uEffectVFR::LifeKeyframe",
    0x727C7279: "rNulls",  # pc-only
    0x7286688A: "MtCollisionTree::Node",
    0x72991E73: "sCollision::SbcInfo",
    0x729BBA7E: "uMinimap::MyDTI",
    0x729D2275: "MtCollada::Param",
    0x729FB5E8: "sSoundN::REQUEST_TYPE",
    0x72A3CA7C: "rClothXml::Index_0",
    0x72A65485: "cCharTblMgr::MyDTI",
    0x72AE54ED: "aTitle::STATUS",
    0x72B401FD: "uPlayer",
    0x72C78F54: "rPlacement::MyDTI",
    0x72CF7DCB: "cCameraNormalInitParam_0::MyDTI",
    0x72E43A26: "rEffectList::EFL_KEYFRAME_U32",
    0x72EA21E3: "uMissionResult",
    0x72EF304D: "MtCollada::Asset::UP_AXIS",
    0x72F19A89: "nodeLink::MyDTI",
    0x731C12F0: "aRoom309::MyDTI",
    0x731D793B: "rEffectList::EFL_PARTICLE_RADIAL_BLUR_FILTER",
    0x732BF0CE: "uPlWeapon::kCnstOfs",
    0x7345C490: "uMotionSe::MyDTI",
    0x734D7173: "cTrans::VolumeTexture",
    0x735CC37C: "cSpline_0::MyDTI",
    0x736A1581: "MtCollada::Optics",
    0x73704205: "MPARAM_POLAR3",
    0x737CBA3A: "MT_ENUM",
    0x73850D05: "rArchive",
    0x738CBD3F: "sCollision::NodeBox",
    0x73920949: "_D3DFORMAT",
    0x73A06E25: "MtCollada::Translate::MyDTI",
    0x73A775F3: "cCameraNormal",
    0x73B18B08: "uEm018BreakHouse::MyDTI",
    0x73C24804: "aMTGSEndDemo::MyDTI",
    0x73CBEF1F: "nodeData::MyDTI",
    0x73D50FD8: "sRender::TILED_STATE",
    0x73DE50CA: "MtCollada::Node::MyDTI",
    0x73E2CEAF: "rEffectStrip::EFS_HEADER",
    0x73F4EC45: "uEffectEdit::WORK_SET_POLYGON",
    0x740F9B4F: "cFrustum::MyDTI",
    0x74221BC8: "sArea::AreaInfo",
    0x7432DC56: "rArchive::RESOURCE_INFO",
    0x7445F0AB: "rEffectSetData::ESD_PARAM_CULLING",
    0x744A826B: "sEffectVFR::MyDTI",
    0x744D502D: "uGroupTable",
    0x74578D89: "aDevil4Grid",  # pc-only
    0x7459E459: "MtCollada::Technique",
    0x745B1933: "rEffectSetData::ESD_SET_HIT",
    0x7477949A: "uWait",
    0x7477AD0F: "uJointVib",  # pc-only
    0x747C9385: "sShader::FUNC_SHADOW_ALBEDO_ALPHA",
    0x747CDCBA: "rMotionList::MOTION_LIST_HDR",
    0x7487F134: "MtFCurve::DescKey",
    0x749EFBC7: "std::iterator",
    0x74B1F5E4: "uPlayer::cHitSlowCtrl",  # pc-only
    0x74BC4D64: "cEnemyResetMgr::MyDTI",
    0x74C5F059: "rEffectList::EFL_MOVE_PATH_CHAIN",
    0x74CAF720: "aMissionTitle::MyDTI",
    0x74E41F1D: "MtCollada::Animation::MyDTI",
    0x74E51BFA: "uOrb00::MyDTI",
    0x74F34173: "uPlayer::cMotCancel",  # pc-only
    0x74FCDB85: "uPlayer::LEVER_DIR",
    0x7503069C: "rEffectSetData::ESD_SET_CULL_POLYGON",
    0x75044C02: "uPlayerNero::kMdlCoat",
    0x750534FB: "CellAtracHandle",
    0x7507E76B: "CellGcmTexture",
    0x75097E34: "uDevilCamera::kVibPreset",
    0x751163FB: "GLAREDEF",
    0x75167EAA: "MtFloat4",
    0x752E18B2: "MtCollada::Light::MyDTI",
    0x7534E4DB: "uCubeMapLight::MyDTI",
    0x753787F6: "uPlayer::JUMP_MODE",
    0x75389616: "rSoundPackageXml::SplitData::MyDTI",
    0x75593F78: "MtXmlReader::Handler",
    0x75636BBC: "MtCollada::Vertices",
    0x75850D9B: "uEffectEdit::WORK_MOVE_PATH_CHAIN",
    0x75AB4F9B: "rPlacementXml::ParamTrack::MyDTI",
    0x75AF12EC: "MtHeapArray_0",
    0x75BC266F: "cCameraPlayer::MyDTI",
    0x75D7EBD7: "MtColorHLS",
    0x760F5837: "rSoundRequest::Header",
    0x760FD842: "uEffectVFR::PRIM_MODEL_DATA",
    0x762DEB07: "rClothXml::Constraint::MyDTI",
    0x763254CA: "MtSerializer",
    0x76366DDF: "aRoom510::MyDTI",
    0x7641660F: "MtCollada::Instance",
    0x7646E594: "cTrans::CMD_DRAW",
    0x76554CA6: "uDevilCock::DEVIL_COCK_PRIO",
    0x765D75BA: "sys_lwmutex_lock_info_t",
    0x7662E147: "uEffectVFR::LINE_FIX_WORK",
    0x76820D81: "rMotionList",
    0x768ED08A: "sShader",
    0x76BFE4E8: "uEffect::BUFF_SIZE",
    0x76C3FD24: "kROUTEQ",
    0x76CA13D7: "uSpotShadowLight",
    0x76D2EF9F: "sCollision::Collider",
    0x76D6A111: "MtREDataReader",
    0x76E5191B: "MtStream",
    0x77188ED9: "rRenderTargetTexture::MyDTI",
    0x7725F64F: "rSoundCurveXml::Curve::MyDTI",
    0x7731D1A8: "std::allocator",
    0x77418F7C: "sShader::ENVELOPE_HANDLE",
    0x774385CF: "MT_MFUNC",
    0x7749B196: "uDevilCamera::ENUM_VIB_PRESET",
    0x7754DD26: "cTrans::TextureBase::LOCKRECT",
    0x77659BA8: "MtCollada::Texture",
    0x776BB04B: "MtCollada::Array",
    0x7786CCA5: "cCamDataHeader",
    0x77ACD113: "rShape::SHAPE_HDR",
    0x77BA714E: "uEffectEdit::WORK_SET_CTRL",
    0x77BBDB6E: "rSoundRequestXml::ElementData",
    0x77D6C9DD: "uHSVFilter::MyDTI",
    0x77E7B756: "uFacial",  # pc-only
    0x77EA0363: "uLevelCorrectFilter::MyDTI",
    0x77ECBD55: "MtCollada::Source::MyDTI",
    0x77F7AE12: "MPARAM_POLAR3KEY",
    0x78081CC8: "uEm015",
    0x7808EA10: "rRenderTargetTexture",
    0x780DF534: "uPlayer::MAJIN_KIND",
    0x7810A672: "uFilter::transImageEx::SCREEN_VERTEX",
    0x78443D05: "sMain::MyDTI",
    0x784F761A: "uEffectVFR::Polyline",
    0x785A06EC: "uModelSky::MyDTI",
    0x785BD903: "uNoiseFogFilter",
    0x786CBB49: "MtFloat3A",
    0x787A7C88: "rFacialPattern::MyDTI",
    0x78906A5D: "rSoundRandomXml::MyDTI",
    0x78A8DB73: "cTrans::CMD_MRT",
    0x78B417D9: "uCinemaScope",
    0x78D243D6: "MtCollada::Asset::MyDTI",
    0x78DE190D: "rModel::MODEL_HDR",
    0x78F2C078: "rCharTbl",
    0x79041D57: "uPlWeapon::LEVEL",
    0x7906F7B0: "sMain::JOB_THREAD",
    0x790E1147: "cCnsRandom",
    0x792B46C0: "uLight",
    0x79403ACB: "cCameraRect3D_0",
    0x7956D885: "rMovieInterMediate",
    0x796B1E4D: "SPU_ARG_TASK",
    0x798BB121: "_D3DPRIMITIVETYPE",
    0x79C4D475: "MtAABB",
    0x79CB8179: "_D3DBLENDOP",
    0x79D12B75: "CellSpursEventFlag",
    0x79D14E38: "sCapture::MOTIONBLUR",
    0x79D1983E: "rDefendStatusData",
    0x79D67846: "rPlacementXml::IntTrack",
    0x79FD2F1D: "uTutorial",  # pc-only
    0x7A167C7B: "std::ldiv_t",
    0x7A1E54C5: "rSchedulerXml::RefTrack::Key",
    0x7A23A3A8: "rEffectSetData::ESD_PARAM_PLACE",
    0x7A363A01: "uTitleB",  # pc-only
    0x7A38BFF4: "rEffectList::EFL_KEYFRAME_COMMON",
    0x7A3A08B4: "CellMSSystemConfig",
    0x7A4E5BB8: "aGame::MyDTI",
    0x7A611B02: "_D3DCUBEMAP_FACES",
    0x7A9A7000: "uAdhesion::ADHESION_NODE_HEADER",
    0x7A9A76AE: "uAdhesion",
    0x7A9C8733: "sUnit::MoveLine::MyDTI",
    0x7A9F0EAF: "uEffectVFR::STRIP_WORK",
    0x7A9F60B9: "sMediator::cPlParamSave::MyDTI",
    0x7AA02BF7: "sRender::MyDTI",
    0x7AB6F83B: "uPlayer::cInterface",  # pc-only
    0x7AD567B0: "uFishEyeFilter",
    0x7ADFDF20: "cTrans::ARRAY_HEADER",
    0x7AF559E7: "uClothSim1D::Node",
    0x7B1057EE: "uStream::MyDTI",
    0x7B238783: "rShape::SHAPE_KEY",
    0x7B281D98: "aRoom310::MyDTI",
    0x7B652FF4: "uDamage",
    0x7B806A6A: "rConfig",  # pc-only
    0x7B92638D: "sResource::RemoteInfo",  # pc-only
    0x7BFC7BC4: "uPlayerDante::kMdlHair",
    0x7C0D50B9: "uPlayer::kRendaParam",
    0x7C10F116: "cEvent",
    0x7C198319: "cUnit::MyDTI",
    0x7C3D9B39: "rClothXml::Index",
    0x7C410A69: "uPauseMenu",
    0x7C61BDFB: "uEm021::MyDTI",
    0x7C8B0681: "MtCollada::Array::TYPE",
    0x7C8CD1A9: "cCamAreaConnect::MyDTI",
    0x7C9B2011: "uGameOverBg",  # pc-only
    0x7CAB0A14: "nodeHead_0::MyDTI",
    0x7CAD2C4A: "sDevil4Main::MyDTI",
    0x7CAF605C: "cTrans::MODE",
    0x7CDF38AE: "EventInfo::CHG_ROOM_DETAIL",
    0x7CE2A5D3: "cEnemyResetMgr",
    0x7CEA278F: "Imitation2DTexture",
    0x7D1530C2: "rSoundSourceMusic",
    0x7D18FCC0: "uEffectEdit::WORK_MOVE_ADD_KF",
    0x7D21FE4A: "cShape::WeightNode::MyDTI",
    0x7D25A9D1: "MtCone",
    0x7D2C887E: "uCloth::MyDTI",
    0x7D3F6F3B: "rEffectAnimation::MyDTI",
    0x7D46C38C: "MtCollada::Entry",
    0x7D548869: "rEffectSetDataList::MyDTI",
    0x7D564877: "uClothSim1D::MyDTI",
    0x7D6F8184: "uEfctDoorSeal::MyDTI",
    0x7D9935CA: "uCoord",
    0x7D9ED899: "MtGeomConvex::MyDTI",
    0x7DDDBD17: "MtGeomTriangle::MyDTI",
    0x7DF56E19: "cTrans::VolumeTexture::MyDTI",
    0x7DF88B30: "sResource::MODE",
    0x7E0262B7: "aRoom509::MyDTI",
    0x7E0A2804: "sResource::RESOURCEWORK",
    0x7E1A784D: "uStageSetBreak",
    0x7E1D866F: "cTrans::VIEWPORT",
    0x7E2DB5EE: "kCollisionTriangle3",
    0x7E33A16C: "rSoundPackage",
    0x7E3DCC96: "uCapsuleShadowLight",
    0x7E3FE6C8: "MtMatrix",
    0x7E62B7C6: "ImitationSurface",
    0x7E6F0FD9: "rEffectList::EFL_PARTICLE_PRIM_COMMON",
    0x7E72DFFD: "sprMap_0",
    0x7EA0A8AB: "rGridEnvLight::NativeBoxInfo",
    0x7EB26724: "uEnemySetCode::MyDTI",
    0x7EBECCD4: "uPlayer::RUN_MODE",
    0x7ECA03E4: "uAdvMovie",  # pc-only
    0x7ECA1716: "uSe",  # pc-only
    0x7ED4C86C: "rSoundEngineXml",  # pc-only
    0x7EDDBB44: "sPathFinding::TracePoint",  # pc-only
    0x7EE5207A: "rSprLayout",
    0x7F0D92CB: "uResultSuji",  # pc-only
    0x7F13118F: "rRouteNode::MyDTI",
    0x7F151759: "sSoundN::Voice::VOICE_TYPE",
    0x7F2579B7: "EFC_PARAM_ANGLE",
    0x7F329990: "rCollada::MyDTI",
    0x7F5904F2: "uPlWpRightHand::uCollisionCtrl::MV_TYPE",
    0x7F5D5596: "MtHeapArray::MyDTI",
    0x7F65D8D1: "uEm011",
    0x7F66AF04: "rSoundSystemFileMSSPUInterMediate",
    0x7F697730: "cSprAnm::MyDTI",
    0x7F6D23D0: "uFacial::MyDTI",
    0x7F757B0A: "uPlWpRightHand::uEffectCtrl::EFCT_TYPE",
    0x7FB24515: "uAttributeSe",
    0x7FF19311: "sResource::Iterator",
}


"""DTI hash table for Resident Evil 5 (PC, re5dx9.exe)"""

DTI_RE5 = {
    0x000343DD: "_XSTORAGE_DOWNLOAD_RESPONSE",
    0x0003986A: "MtSerializer::OBJECTDATA",
    0x0006D48D: "_DMREGISTERPERFCOUNTERPARAMBLOCK",
    0x000DA93E: "MPARAM_VECTOR3",
    0x001B3BDC: "_XMHALF4",
    0x00252A4A: "cSetInfoOmWallStick",  # pc-only
    0x00254F57: "CONTENTENCRYPTIONOBJEXT2",
    0x0026E7FF: "rChainCol",
    0x002893DF: "_XMFLOAT3",
    0x002AA9B8: "cNetEmc0",  # pc-only
    0x003457AB: "DCTMode",
    0x00347F62: "cAIGraph",  # pc-only
    0x0036684A: "cOmBldgAction_break",  # pc-only
    0x003A98DB: "IXAudioRefCount",
    0x00443A21: "cEm10ActRun",  # pc-only
    0x0048CC97: "_D3DBASISTYPE",
    0x004A7CD7: "CXStorageEnumerate",
    0x004BD1EC: "sParameter::LEVEL_PARAM_F",  # pc-only
    0x004F8CB6: "uBioHazeFilter",  # pc-only
    0x004FD788: "uOm0026::cActWaitL",  # pc-only
    0x0059CEDF: "_IO_COMPLETION_BASIC_INFORMATION",
    0x005A8F9D: "threadlocaleinfostruct",
    0x005AF68E: "rSoundStreamRequest::SOUND_STREAM_DISK_READ_AREA",
    0x005F8E26: "rCloth::MyDTI",
    0x006098FB: "uOm08b8_Limited::cActBase",  # pc-only
    0x0060EEB7: "rEffectList::MOVE_OPTION_FLAG",
    0x00664D74: "cOm0200ActFinish",  # pc-only
    0x0066F065: "cEm65ActBox",  # pc-only
    0x00675E79: "COHER_BASE_PM4",
    0x0068F2B1: "XGI_USERGETPROPERTY_MSG",
    0x006943CA: "tagPOINTS",
    0x006FFE6E: "_XONLINE_ATTRIBUTE_STRING",
    0x00736805: "SCRATCH_REG4",
    0x00736CAE: "JOINT_TYPE",
    0x007391A7: "_SET_USER_SETTINGS2_REQUEST_STRUCT",
    0x0074D357: "PA_SC_FIFO_SIZE",
    0x00770576: "PCIE_PERF_CNTL_EVENT0_PORT_SEL",
    0x0078170C: "cEmc2ActDownCamera",  # pc-only
    0x00797851: "HZ_PERFCOUNTER1_HI",
    0x007AA0DA: "cEm32ActThreat",  # pc-only
    0x007CF76F: "XAUDIO_POOL_TAG",
    0x0080BEA1: "HeapManager",
    0x0081C3D5: "uOm0912_s119Tram::cActPlFall",  # pc-only
    0x00820811: "GPUINITIATOR",
    0x008290B1: "MtContact",
    0x0084F2F0: "D3D::CPixelShader",
    0x00874277: "sEffectBase::FilterControl::__vftable",
    0x0089EAFD: "uModel::Motion::ATTRIBUTE",
    0x008AEA71: "rEffectSetData::MOVE_TYPE",
    0x008B33AA: "XONLINE_MEDIA_URL_TYPE",
    0x008D853C: "CP_CSQ_IB1_STAT",
    0x0091CD1B: "XHV_CODEC_HEADER",
    0x009419FC: "_XBMOVIE_CAPTURE_VIDEO_INFO",
    0x00974B8E: "CP_RT5_COMMAND",
    0x0098A5C0: "_CONTENT_DETAILS_REQUEST",
    0x009B3FDE: "ID3DXPMeshVtbl",
    0x009C82E9: "_DXVA_COPPStatusSignalingCmdData",
    0x009DA814: "TP2_CHECKSUM_PIXEL_3",
    0x00A25EE3: "MtGeometry::Type",
    0x00A69EF8: "cEm8cAtkGroundHitLoop",  # pc-only
    0x00A8F922: "cOmJeepAction",  # pc-only
    0x00AF30B8: "cEm6cAction",  # pc-only
    0x00B01145: "cOmCoopDoorAction_pl_act_push_kick",  # pc-only
    0x00B2777D: "IXoCallback::__vftable",
    0x00B2CA03: "_D3DXPARAMETER_TYPE",
    0x00B30E62: "cEm61ActDieIce",  # pc-only
    0x00B42536: "cEm80ActInjection_PL2",  # pc-only
    0x00B5CF10: "_IMAGE_COFF_SYMBOLS_HEADER",
    0x00C83DA4: "GPU_DESTINATIONPACKET",
    0x00D30A38: "UVBASE_SESSION_INFO",
    0x00D50275: "sCollision::Sbc::Parts::MyDTI",
    0x00D5908B: "_XMATCH_DEAD_XBOX",
    0x00D93AFF: "AZ0_COPY_STATE_DWORD2",
    0x00DA27AD: "uOmSwitchPulley::cActPulleySwitchOn",  # pc-only
    0x00DB3247: "XAUDIO::CAutoPerfCounter",
    0x00E29B89: "SQ_INSTRUCTION_ALU_2",
    0x00EAAF30: "_XCREATEPROFILEUI_PARAMS",
    0x00FAD544: "uOmSwitch::cActWaitToOn",  # pc-only
    0x00FE7B64: "XAUDIO::CFrameBuffer",
    0x00FEF78C: "rEffectList::KEYFRAME_STATUS",
    0x01026AEE: "rEffectList::EFL_PARTICLE_CLOTH_POLYGON",
    0x0102DB6B: "rEffect2D::ResourceInfo",
    0x01036ADA: "uOm1317_S109_Glass::cActWait",  # pc-only
    0x010638F6: "PCIE_ENH_ADV_ERR_RPT_CAP_HDR",
    0x0108B76B: "FSB_LX_DEBUG_LO",
    0x010DB3D6: "_FXLRENDERSTATEENTRY",
    0x010E44F6: "_FILE_SECTOR_INFORMATION",
    0x01122995: "_Q_DEQUEUE_MSG_INTERNAL",
    0x011442EE: "_MIID_OFFERID_PAIR",
    0x01145649: "_s__ThrowInfo",
    0x0114E638: "cEm84ActDashBgn",  # pc-only
    0x01152EF8: "uBioActorPL01Simple",  # pc-only
    0x0121E97E: "cOmJeepAction_om_act_barricade_battle",  # pc-only
    0x01252D4F: "_FP_IEEE_COMPARE_RESULT",
    0x0129232A: "rEffect2D::E2D_KEYFRAME_U32",
    0x012D97DA: "PatConnection",
    0x012E47B0: "uEffectVFR::PolygonStrip",
    0x01336641: "cOmPileAction_break",  # pc-only
    0x013384EE: "tagWMAFileLicParams",
    0x01403FA4: "CLIPPER_DEBUG_REG03",
    0x01418FD0: "CCodingStats_WMA",
    0x0141D77C: "RB_COPY_DEST_BASE",
    0x0147DC41: "cEm22Action",  # pc-only
    0x014D4CCF: "cEm10ActAtkGunBombSit",  # pc-only
    0x0151D8CB: "CP_RT5_SIZE",
    0x01525F5F: "CLIPPER_DEBUG_REG10",
    0x01545668: "cEm34ActSmoke",  # pc-only
    0x01547F27: "IOC_PERFCOUNTER0_HI",
    0x0154EEA5: "XAUDIO::CDebug",
    0x0155DCD4: "rEffectList::EFL_KEYFRAME_INDEX",
    0x01572A19: "IOC_PERFCOUNTER0_LOW",
    0x01583378: "_XMARKETPLACE_ASSET_ENUMERATE_REPLY",
    0x016066DC: "uAdhesion::MyDTI",
    0x01662DD0: "cPositionEvaluationPlayerVisibility",  # pc-only
    0x016CBD6F: "rEffect2D::RANGE_DIR_TYPE",
    0x016F638D: "IXAudioRouterEffectVtbl",
    0x01771324: "cBioAIPathFinding",  # pc-only
    0x0178C728: "MPEG_INFO",
    0x017A550D: "rLotSelectorMove",  # pc-only
    0x017AC8D9: "PARSEROUTPUT",
    0x017DEA16: "std::_Mutex",
    0x0181DF10: "uCapsuleShadowLight::MyDTI",
    0x018735A6: "rHkMaterial",  # pc-only
    0x01889CAB: "cEm30ActTearHead",  # pc-only
    0x018AA3F7: "FSB_TR_ERRCAP",
    0x018ADBC7: "rSoundPackage::Split",
    0x018E8102: "cEm42SActMotOnce",  # pc-only
    0x01910DA9: "std::exception::__vftable",
    0x01913CBF: "PIX_INDEX",
    0x019A59C5: "_WMAEncOpts",
    0x019CDBD5: "uEffectEdit",
    0x01A069CD: "CXStorageDelete",
    0x01A0B746: "_XTHREAD_NOTIFICATION",
    0x01A26BA9: "_SECURITY_TOKEN_PROXY_DATA",
    0x01A42127: "FSB_TR_CTRL_AND",
    0x01A64114: "_XSHOWMARKETPLACEUI_PARAMS",
    0x01A76E24: "cOmWindowAction_fence_em10",  # pc-only
    0x01A7D157: "cSetInfoOmDive",  # pc-only
    0x01A7FEA4: "cEm83ActPinionedAtk",  # pc-only
    0x01B34E3A: "RB_HSIO_DLL_ADJ3",
    0x01B447D8: "cEm10ActAtkDashOneHand",  # pc-only
    0x01B63947: "_XCONFIG_CONSOLE_SETTINGS",
    0x01B828F5: "uOmSwitchPulley::cActPulleyCome",  # pc-only
    0x01B92B31: "r2Texture::MyDTI",
    0x01BE39F5: "cOm0200ActWait",  # pc-only
    0x01BE61AF: "cEm40ActTakeBlow",  # pc-only
    0x01C17FD9: "TP3_CHECKSUM_PIXEL_1",
    0x01C28576: "_XONLINE_MATCH_SPLITRESULT",
    0x01C8B9C3: "D1SCL_VERT_FILTER_SCALE_RATIO",
    0x01C8CAD6: "cLinkUnitPosAngle",  # pc-only
    0x01C98E4C: "CONTENTDESC",
    0x01CB01C8: "CCalFileStream",
    0x01D28F6D: "_COPP_StatusFlags",
    0x01D2DB96: "ID3DXBaseMeshVtbl",
    0x01D37491: "sArea::MyDTI",
    0x01D56A91: "SQ_INSTRUCTION_CF_ALLOC_1",
    0x01D79C02: "TCF_PERFCOUNTER4_SELECT",
    0x01DBA113: "uEffectEdit::MoveMul",
    0x01DE8CB4: "cEm3403ActBlow",  # pc-only
    0x01E9C593: "XUIObjectData",
    0x01ECEA19: "cEmA2Rimontyotyu_Ok_PL",  # pc-only
    0x01F03A56: "LIVEBASE_SETPRESENCE_MSG",
    0x01F1FA49: "CXStorageUploadWorker::RESOLVE_NAME_RESPONSE_BUFFER",
    0x01F3C3DF: "DCPERFREGISTER",
    0x01F40843: "_XHTTP_REQUEST_DOWNLOAD_TO_FILE_PARAMS",
    0x01F464A0: "DRMINSTANCE",
    0x01F90739: "cOmDoorActOpenHand",  # pc-only
    0x01FA3CC8: "XUIMessageSourceImage",
    0x02006DB5: "RENDERERMSGINFO_SETBUFFERSIZE",
    0x0201006F: "uLayoutSpr",  # pc-only
    0x0209890F: "sTool::MyDTI",
    0x020C978E: "uOm1303_Truck::cActEnd",  # pc-only
    0x0211502C: "_CEA861_AUDIO_INFOFRAME",
    0x021647E5: "rSoundRequest::ReadHeader",
    0x0217BF19: "uOm1316_BackupHeli2::cActWait",  # pc-only
    0x0217DF74: "cEm44ActAtckScissor",  # pc-only
    0x02185599: "NetworkSessionManager::Chat",
    0x021A7492: "NetworkConnectionMcs",
    0x021F022C: "FSB_TR_DEBUG_LO",
    0x0221DC13: "XHVACTIVATIONOP",
    0x022495C9: "GPUGROUPCONV",
    0x02303F28: "uEnvMap::MyDTI",
    0x0232727E: "_FSCACHE_EXTENSION",
    0x0235FC7E: "_Q_LIST_ITEM",
    0x02371150: "_DVD_XGD2_DISC_AUTH_RESULT_LBA_FAILURE",
    0x02376A53: "XUIMessagePlayVisual",
    0x023B641D: "cEm32PlEvent_MountMiss",  # pc-only
    0x023DB1C3: "MtCollada::Primitive",
    0x023EC4A3: "std::_Char_traits_base",
    0x02401783: "_LUID_AND_ATTRIBUTES",
    0x0241E1FE: "FSB_TLA_COUNT4_INIT",
    0x024C28B6: "EXTSTREAMPROP",
    0x02521B3C: "cTrans::CMD_STREAMOUT",
    0x02583C25: "sPrim::FUNC_PRIM_MASKMAP",
    0x025D8CF2: "MtLogisticMap",
    0x02604CF2: "rSoundSource::__vftable",
    0x026619DF: "BIU_PERFCOUNTER1_SELECT",
    0x026704C7: "rSoundStreamRequest::StreamInfo",
    0x026B13D8: "RTS_MISC",
    0x026C04F6: "rSoundCurveSet::MyDTI",
    0x02745A7B: "RB_SIDEBAND_RD_ADDR",
    0x0277F151: "SQ_CONSTANT_VFETCH_0",
    0x027988EF: "_D3DXINTERSECTINFO",
    0x02799B33: "_UCODE_FLOAT16",
    0x027DD36C: "D1OVL_SURFACE_ADDRESS",
    0x028015FF: "cEm84ActDownStrippedAtk",  # pc-only
    0x02833703: "rEffectStrip",
    0x0287631D: "MC0_TUNING_1",
    0x028B2FA9: "_QUAD",
    0x028C1E6A: "cAIDynamicPathFinding::GroupManagement::Group",  # pc-only
    0x028D26F4: "uOmS705ceil::cEvActKillEm",  # pc-only
    0x028FEB48: "cEm45Action",  # pc-only
    0x029089C9: "cPlAction_pl_act_coop_treat_rec",  # pc-only
    0x0295A80D: "XMALOOPREGION",
    0x02968765: "NetworkLayer::AreaReceive",
    0x0297B586: "uOm1316_BackupHeli::cActBase",  # pc-only
    0x029EFCCA: "_RTL_PROCESS_LOCKS",
    0x029F355A: "rEffectSetData::ESD_SET_LENS_FLARE",
    0x02A0EE23: "sCollision::cColArray2",
    0x02A211DF: "_USER_XNAME",
    0x02A4EE36: "rEffect2D::COLOR_CORRECT_TYPE",
    0x02A700C7: "XGI_READWRITETILE2_MSG",
    0x02A96AC8: "_D3DTEXTURETRANSFORMFLAGS",
    0x02B39460: "FSB_LX_CTRL_AND",
    0x02B5D635: "uCoord::PARENT_FLAG",
    0x02B733C5: "cScenarioArg_Flag",  # pc-only
    0x02B83BFD: "cEm8cAtkArmUp",  # pc-only
    0x02B91ECD: "LIVEBASE_EXPIREMARKETPLACECOUNTSCACHE_MSG",
    0x02B9FAC6: "rShader::CONSTANT_INFO",
    0x02C0E6E8: "rEffectList::RANGE_DISPERSE_TYPE",
    0x02C1B702: "rSoundStreamRequestXml::ElementData",
    0x02C4F91C: "NetworkSessionManager::Filter",
    0x02C53246: "cNetEm52",  # pc-only
    0x02C6E4F6: "cDemoTitle",  # pc-only
    0x02C6EED4: "cEm20ActAtkExecCatch_PL",  # pc-only
    0x02CE7D9B: "CCalJpegDecoder",
    0x02DA5F91: "cPositionFilterDoughnutAroundNearPos",  # pc-only
    0x02DCA74D: "CCalSubInfo",
    0x02E2E7ED: "D1SCL_HORZ_FILTER_INIT_CHROMA",
    0x02E3DE9D: "cEm10ActAtkGunShotSG",  # pc-only
    0x02E4C6F9: "XAUDIOCHANNELMAP",
    0x02E8DF69: "RB_DEBUG_0",
    0x02E9C29D: "_DXVA_DeinterlaceBlt",
    0x02EEF406: "cNetEm41Arm",  # pc-only
    0x02F016F0: "tagCMSMtoN",
    0x02F79302: "_OVERLAPPED",
    0x02F9D21A: "uOmCoopTreasure::cActOpened",  # pc-only
    0x0300053C: "CXStorageTask",
    0x03038592: "cEm84ActRoll",  # pc-only
    0x0303A343: "uOma00b_LaserArea::cActSleep",  # pc-only
    0x03073AE8: "_D3DBACKBUFFER_TYPE",
    0x030FCB6B: "_KINTERRUPT_MODE",
    0x0312D5CD: "NetworkPeerEcho",
    0x0315E81F: "rSoundDirectionalSet",
    0x0319B7A0: "cEm22ActWait",  # pc-only
    0x031F8368: "MtGeomLineSegment",
    0x0322F7E0: "MtQuaternion",
    0x0323EE39: "cEm61ActGlide",  # pc-only
    0x0328B8AF: "sRender::DAC_TYPE",
    0x0328E34B: "sCollision::Node",
    0x03307D38: "CXHttpDownloadToFile",
    0x0333D2D0: "uChain::JointWork::MyDTI",
    0x03368EE8: "uShadowLight",
    0x033C1B2D: "XAUDIO::CMutex",
    0x033DFF9F: "sCollision::JobParam",
    0x033EC11B: "XDVO_2ND_CRC_SIG",
    0x03433D13: "sShader::TEX",
    0x0347E194: "_WMAFormatInfo",
    0x03490D14: "ID3DXBuffer",
    0x034DE4D4: "rChainCol::MyDTI",
    0x03539FD5: "Status",
    0x0357D5CD: "MtCollisionTree",
    0x03587FEB: "IShaderPDBBuilder::__vftable",
    0x035B066B: "_STFC_STATS",
    0x035FD29C: "rSoundSpeakerSetXml::NativeData",
    0x0361F932: "_DXVA_ConnectMode",
    0x0369750B: "PACKET_QUEUE",
    0x036A31B2: "CP_RT6_POLL_ADDRESS",
    0x036E477D: "_IMAGE_RESOURCE_DATA_ENTRY",
    0x036E4D98: "EFC_PAT_LIST",
    0x0370E4FC: "_KWAIT_BLOCK",
    0x0379902E: "_D3DOCCLUSIONSTATS",
    0x037BD07A: "rSoundCurveXml::TargetPlatform",
    0x037D33E3: "_XONLINE_QUERY_ATTRIBUTE_SPEC",
    0x037E4BC4: "CP_ME_NRT_DATA",
    0x03827BC0: "cEm10ActDmgGGLeg",  # pc-only
    0x038525FB: "_MODE",
    0x03874D60: "cEm84PlEvent_Caught",  # pc-only
    0x03901BD2: "cOmLadderActionV_climb",  # pc-only
    0x03945ECA: "XECRYPT_RSAPUB_1536",
    0x0395FDD1: "OLDINDEXENTRIES",
    0x0397680E: "cEm0bActDieCatchBomb",  # pc-only
    0x03979B5C: "uOma00c_UroAction::cActBase",  # pc-only
    0x0397BF9C: "uOmS508_Break::cActEnd",  # pc-only
    0x0399EDB8: "cEm84ActDmgNormalM",  # pc-only
    0x039A4F5F: "XAUDIO::XAUDIOSRCSOURCE",
    0x039AA1AD: "cEm10ActDmgAtFaceUp",  # pc-only
    0x039BB503: "uOm0927_Crane::cActMoveDC",  # pc-only
    0x039C2BC9: "CBitSequence",
    0x039D71F2: "rSoundReverbTable",  # pc-only
    0x039F9B2F: "cOmAction_om_act_wait",  # pc-only
    0x03A0FCDB: "sCamera::Viewport::TONEMAP_TYPE",
    0x03A10C9C: "XAUDIO::CAutoLock",
    0x03A9F2A3: "cEm30ActLand",  # pc-only
    0x03AFCB43: "rModel::MODEL_INFO",
    0x03B1C65F: "uOm0026::cActStartR",  # pc-only
    0x03BBE03D: "LB_DEBUG_BLOCK_ID",
    0x03BC7BA6: "DC_HSYNC_DEBUG_TEST",
    0x03BDC59F: "_P_IS_AFFILIATE_REPLY_MSG",
    0x03BE9BB1: "RBBM_STATUS",
    0x03C0215F: "_XSIGNATURE_ACKNOWLEDGE_LICENSES_DELIVERY_REQUEST",
    0x03C53E71: "uModel::MaterialGroup::MyDTI",
    0x03C7EB23: "_D3DXMESHCONTAINER",
    0x03C94D8A: "MtCollada::Optics::MyDTI",
    0x03CE1F88: "tagWMCMetaDataEntry",
    0x03D8278B: "_WMAEncFormatOpts",
    0x03E90185: "FSB_LX_PMC4_AND",
    0x03E9C2A0: "_XSIGNATURE_GENERIC_BLOCK",
    0x03EA49DE: "NetworkSession::SessionId",
    0x03ED9ADA: "XGI_SESSIONSTATE_MSG",
    0x03EEAD63: "cWpActionSub",  # pc-only
    0x03F1F881: "MtGeomOBB::MyDTI",
    0x03F2984A: "PA_CL_CNTL_STATUS",
    0x04023766: "uOmCoopJumpBroad::cActWaitJumpReadyCancel",  # pc-only
    0x040935C1: "cPositionEvaluationVisibilityThroughToPos::Work",  # pc-only
    0x04124E96: "rSoundSourceSE",
    0x0415145A: "TP1_CHECKSUM_PIXEL_1",
    0x04153A90: "_BASIC_TITLE_INFO",
    0x041691A5: "_PixCCVideoEncodingType",
    0x041C8F30: "XUIMessageSetCurSel",
    0x042509AA: "LIVEBASE_UPDATEACCESSTIMES_MSG",
    0x042793B0: "PA_SC_PERFCOUNTER1_LOW",
    0x042C4B84: "CXLiveAsyncTaskInternal",
    0x04310312: "AZ0_MRT_STATE_DWORD0",
    0x043144B5: "DM_FILEEVENT_API",
    0x043401B6: "NetworkLayer::Chat",
    0x04348226: "rNavigationMeshDae::Polygon",  # pc-only
    0x043526DB: "D1CRTC_OVERSCAN_COLOR",
    0x0435758B: "MT_IF",
    0x043780CF: "uActorModel::EffectEmitter::POS_TYPE",
    0x0437B662: "CP_RT14_BADR",
    0x0438166E: "_UCODE_DEBUGGER_PARAMETERS",
    0x0439A3FA: "CXLiveNotification",
    0x043E9319: "uEffectVFR::Filter",
    0x0442E131: "cEm32ActBack",  # pc-only
    0x0443DDBF: "_XONLINE_PRESENCE",
    0x04480FD9: "cFSMTaskCtrl",  # pc-only
    0x04560735: "uSynchroAdhesion",
    0x045BEAA7: "rShader::HEADER",
    0x045C1512: "CP_PFP_RT_UCODE_DATA",
    0x0468E958: "MtCollada::COLLADA",
    0x046D2256: "rEffect2D::PLACE_TYPE",
    0x046F3A30: "NetworkSessionManagerPat::MemberInfo",
    0x04728FAC: "AZ0_LOOPBACK_PATTERN0PHS1",
    0x0473247E: "_D3DTESSPRIMITIVETYPE",
    0x0473464C: "D1SCL_TAP_CONTROL",
    0x04736C14: "ID3DXEffect",
    0x0474C0C3: "uOmLaserMirror::cActLeave",  # pc-only
    0x0475AF33: "CGioBase::__vftable",
    0x0477D511: "cEm84ActDmgCore",  # pc-only
    0x047BEF14: "HTASK__",
    0x047DB562: "GPUTEXTURESIZE_1D",
    0x047DF17C: "FPLL_CNTL_REG",
    0x047E5805: "tagEMB_BMainLoop",
    0x047FF28E: "FSB_TX_PMC4_OR",
    0x0480BE56: "cEm0cActDieBlow",  # pc-only
    0x04817154: "_FXLPA_CONTENT",
    0x04882813: "cTrans::OcclusionQuery",  # pc-only
    0x048C6501: "COHER_SIZE_HOST",
    0x048C92F6: "NellyVAD_mblk",
    0x0490E287: "sSoundN::ENTRY_COMMAND",
    0x049261BA: "_DVD_XGD2_AUTH_RESULTS",
    0x0492FD43: "SQ_INST_STORE_MANAGMENT",
    0x049CECAD: "uSchedulerEdit",
    0x04A8635F: "cEm62ActJump",  # pc-only
    0x04AC62D2: "AZ1_LOOPBACK_PATTERN_CONTROL",
    0x04AD878F: "aS202::cActFallBridge",  # pc-only
    0x04ADDDA4: "CHuffmanTable::__vftable",
    0x04B68E2E: "cOmBreakAction_message",  # pc-only
    0x04B85A97: "XGI_SESSIONSPLIT_MSG",
    0x04B9A7BB: "MtProperty::ATTR",
    0x04BA1170: "_SECURITY_DESCRIPTOR_RELATIVE",
    0x04BA87FE: "rEffectList::EFL_KEYFRAME_VECTOR",
    0x04BC58AD: "GPUTEXTURESIZE_STACK",
    0x04BE4EF8: "NetworkConnectionStable::InitArg",
    0x04C15DCF: "PatInterface::LayerUser",
    0x04C41968: "_ECD_DESCRIPTOR",
    0x04C4264B: "XAUDIO::CEngine::CEngineVoiceList",
    0x04C5C482: "XMSG_FLAGS",
    0x04C63C34: "uToneMapFilter::GlareDef",
    0x04D65F66: "cPlAction_pl_act_damage_knock_down",  # pc-only
    0x04E47689: "rAIFSM::ParamConstString",  # pc-only
    0x04F0BA74: "_D3DSURFACE_DESC",
    0x04F1545E: "uOm08b3_S203Elev::cActOpen",  # pc-only
    0x04F9FE7A: "VGT_MAX_VTX_INDX",
    0x0504F847: "XAUDIOENGINEINIT",
    0x0506E617: "sPad::PAD_DATA",
    0x0507C3C9: "ROM_PAR_DATA_REG",
    0x050805F6: "D3dCpuDrPixCounters",
    0x050B4CF5: "MtFrustum",
    0x050DD2BB: "cEm62Action",  # pc-only
    0x0511213D: "_D3DXCALLBACK_SEARCH_FLAGS",
    0x05116DB0: "rEffectSetData::COLOR_CORRECT_TYPE",
    0x0511CC0F: "Q_MSG_TYPES",
    0x05182110: "D1SCL_VERT_FILTER_INIT_BOT",
    0x051B153D: "CXuiElementImplBase::__vftable",
    0x051B5689: "GPUQUANTMODE",
    0x051C1CAD: "HPEN__",
    0x0521698C: "cEm10ActAtkOneHand",  # pc-only
    0x052817BF: "_SYSTEM_ALARM_OBJECT_ACE",
    0x052898A8: "UnDecorator",
    0x052E5370: "PA_SC_DEBUG_QPP_0",
    0x052EF44E: "XAUDIO::CReverbEffect",
    0x052F99F3: "RB_COLOR_MASK",
    0x05306CC3: "sPrim::Material::PrimType",
    0x05345F60: "XDVO_2ND_CRC_MASK_SIG",
    0x0537993E: "FSB_TLA_COMPR_CARE_MASK0",
    0x053B93E7: "MtDefaultAllocator::MyDTI",
    0x053EDAE1: "cEm82ActNoMove_PL",  # pc-only
    0x053F958D: "uOm1316_BackupHeli2::cEvActOptA_Shoot",  # pc-only
    0x0543F632: "MtCollision::SimplexSolver::UsedFlag",
    0x0549C397: "TP0_CHECKSUM_PIXEL_3",
    0x054C00E1: "XONLINE_SUBSCRIPTION_STATUS_TYPE",
    0x054E4129: "sSoundN::__vftable",
    0x054F8485: "_FILE_MOVE_CLUSTER_INFORMATION",
    0x0550FAA7: "HZ_PERFCOUNTER0_LOW",
    0x0554F5F5: "SQ_WRAPPING_0",
    0x055575B4: "uOmDive::cActWait",  # pc-only
    0x055F5F93: "cEm62ActEgg",  # pc-only
    0x055F85A1: "CCalBase::IMAGE_FORMAT_TYPE",
    0x0560C07B: "_D3DSVERROR_TYPE",
    0x056CEE4D: "MtSerializer::HEADER",
    0x056D7ED5: "rEffectStrip::VERTEX_PARAM",
    0x056DD4DF: "AZ1_MRT_STATE_DWORD2",
    0x0571DC08: "_ASYNCIO",
    0x05731ACD: "DEVICESTATE",
    0x0573C430: "RecordHeader",
    0x057D56D9: "XAUDIO::CSourceVoice",
    0x057F2191: "VC_FIFO_DEPTHS",
    0x058102EB: "SOFT_STRAP_CNTL",
    0x0583CD64: "CP_PERFCOUNTER_LO",
    0x05842208: "XNQOSLISTENSTATS",
    0x058DC69B: "rSoundPackage::Program",
    0x058DF95A: "cAIPathFinding::Node",  # pc-only
    0x058F9DAE: "rSoundDirectionalSet::MyDTI",
    0x0596936C: "uModel::RenderInfo::VFCULL_LEVEL",
    0x059A2F18: "rEffectList::EFL_PARTICLE_MODEL",
    0x059B11CF: "FSB_TX_CTRL_OR",
    0x059D3B5F: "D1GRPH_COLOR_MATRIX_COEF_1_4",
    0x059D92F8: "TCF_PERFCOUNTER0_SELECT",
    0x05A00E33: "rArchive::CompressStream::MyDTI",
    0x05A4FA4F: "uPointShadowLight::MyDTI",
    0x05A8CE89: "cActRanOver",  # pc-only
    0x05ABDFC5: "PCIE_PERF_LATENCY_REQ_ID",
    0x05AD1358: "GPUCLAMPPOLICY",
    0x05AF251C: "rEffectSetData::LINE_TYPE",
    0x05B4936D: "cEm83ActDmgGuard",  # pc-only
    0x05B88396: "cEm6fActCircleFly",  # pc-only
    0x05BA96A4: "cNetEm45",  # pc-only
    0x05BE9EB8: "CP_ME_CNTL",
    0x05C3945A: "RB_SIDEBAND_WR_ADDR",
    0x05C58305: "CPolyphase",
    0x05C60F83: "cEm52ActPickup",  # pc-only
    0x05C7C4C4: "cPlAction_pl_act_coop_item_load_2_second",  # pc-only
    0x05CAB0D8: "_XINPUT_KEYBOARDSTATE",
    0x05CB3970: "cEm22ActEngine",  # pc-only
    0x05CB6BBD: "std::__non_rtti_object",
    0x05CD5B7A: "PCIE_LC_N_FTS_CNTL",
    0x05CE291D: "uEffectVFR::TRANS_TYPE",
    0x05CE439F: "RTS_WD_EDGE_DIST_MSBS",
    0x05CEB12D: "MtCollada::Material::MyDTI",
    0x05CFB709: "AdjustDecRangeWMVA_OnePlane_ctl",
    0x05D2962E: "_DM_GET_INPUT_CAPABILITIES",
    0x05E89F76: "cFSMOrder::FuncParamBGM",  # pc-only
    0x05F0EFBA: "rSoundSourceXMA::XMA2WAVEFORMAT",
    0x05F37FA2: "BIOS_5_SCRATCH",
    0x05F70A99: "SQ_INTERPOLATOR_CNTL",
    0x05F83488: "_QUERY_UPDATEID_REQUEST",
    0x05FD2D67: "cEm10ActAtkSitGunReload",  # pc-only
    0x05FFE4BD: "_FXLSHADERSTATEENTRY",
    0x06013A2D: "CXuiTabScene",
    0x06045563: "STARDEF",
    0x06062CB4: "XHVOUTPUTEFFECT",
    0x060834C2: "AZ1_LOOPBACK_PATTERN0PHS2",
    0x060BCA4B: "uColorCorrectFilter::Corrector::MyDTI",
    0x060F46EA: "uOm0201_Piano::cActWait",  # pc-only
    0x0615C107: "uFilter::BLENDOP_TYPE",
    0x06178B82: "_FILE_FS_LABEL_INFORMATION",
    0x0619EF31: "D1GRPH_COLOR_MATRIX_COEF_3_4",
    0x0619F792: "CP_CSQ_IB2_STAT",
    0x061AFB2F: "D3D::DebugAllocationNode",
    0x061FFC89: "rCollision::Triangle",
    0x0621C986: "MASTER_INT_SIGNAL",
    0x0623D0D2: "cTrans::Technique::HEADER",
    0x06299794: "uOm1316_BackupHeli2::cEvActOptA_Wait",  # pc-only
    0x062DFBBD: "CLIPPER_DEBUG_REG07",
    0x0635CDDE: "sGpuParticle::PacketVB::__vftable",
    0x06362BAA: "PA_SC_PERFCOUNTER3_SELECT",
    0x0636C270: "sPrim::FUNC_PRIM_FOG",
    0x06383F17: "cEm80NageEscape_PL",  # pc-only
    0x063AF4C7: "sGpuParticle::MODE",
    0x063F9B46: "CLIPPER_DEBUG_REG14",
    0x06400EDF: "_D3DPSHADERCAPS2_0",
    0x0643AABA: "_XMUSHORT2",
    0x064832F2: "tagEMB_PMainLoop",
    0x064A3AD8: "rSoundSpeakerSetXml",
    0x064F9B5F: "VGT_DEBUG_CNTL",
    0x06556643: "_FPO_DATA",
    0x065857E4: "MtHalf2",
    0x065A204B: "_DM_SWAPDISC_STATUS",
    0x065DE29C: "rEffectSetData::ESD_SET_LINE",
    0x0660885A: "GPU_MISCPACKET",
    0x06665DF6: "rAIFSM::ParamConstS32",  # pc-only
    0x0666FEEE: "_RTL_HEAP_TAG",
    0x06687527: "_XSHOWFRIENDSUI_PARAMS",
    0x066BCAA6: "RlcTblType",
    0x0675C7D1: "uCamera::__vftable",
    0x067AFF04: "uOma00e_UroWall::cActBack",  # pc-only
    0x067EF786: "PIX_NEXT_GPU_CHUNK",
    0x067F353E: "tagWMCDecodeDispRotateDegree",
    0x06819F07: "CompareFrag",
    0x06864E3E: "DCP_LB_DATA_GAP_BETWEEN_CHUNK",
    0x0687B895: "cWpAction_wp_act_gunemp_ready_loop",  # pc-only
    0x068932A3: "uOmS204CrouchPoint::cEventActCrouch",  # pc-only
    0x068B2C91: "_STF_CREATE_PACKET",
    0x0691390B: "uOm1316_BackupHeli2::Point",  # pc-only
    0x0692533F: "SQ_PERFCOUNTER3_LOW",
    0x06938977: "cEm84PlEvent_PinionOff",  # pc-only
    0x069827B7: "XUIMessageGetHtmlLinkVisited",
    0x06A1C820: "XAUDIO::CPerfCounter",
    0x06A34B6C: "cOmJeepAction_om_act_ev_01",  # pc-only
    0x06A57556: "PatInterface",
    0x06A69F9B: "cEmAction",  # pc-only
    0x06A7EC42: "sShader::PIPELINE_SHADOW_RECV",
    0x06AD1B8E: "XUI_LISTITEM_LAYOUT",
    0x06B0FCEE: "sSoundN::MultiBandEQUnit::MyDTI",
    0x06BBC320: "cPlAction_pl_act_knife_attack",  # pc-only
    0x06BBD189: "VGT_OUTPATH_SELECT",
    0x06BCA421: "_UCODE_CONSTANT_TABLE",
    0x06BD57A0: "sCollision::MOVING_SCR_PARAM",
    0x06BE4253: "_FILE_BASIC_INFORMATION",
    0x06BF69C9: "_STFC_VOLUME_DESCRIPTOR",
    0x06C17834: "cEm52ActOverturn",  # pc-only
    0x06D25B4B: "cEm34ActRamp",  # pc-only
    0x06D3AA11: "cEm43ActHookA",  # pc-only
    0x06D682EA: "cEm80ActKataNg_PL",  # pc-only
    0x06D87FA0: "cEm10ActDeadArmyBurn",  # pc-only
    0x06D937CD: "GPU_SAMPLECOUNT",
    0x06DBB258: "_P_TEAM_RECRUIT_MSG_NAME",
    0x06DE8A23: "RB_HSIO_DLL_ADJ7",
    0x06E1C8C5: "cEm45ActPlagaDie",  # pc-only
    0x06E87C7E: "cAIFSMParameter",  # pc-only
    0x06F2D734: "sVibration::VibFlag::__vftable",
    0x06F35BC2: "sShader::DEBUGVIEW",
    0x06F402FF: "COHER_STATUS_RT",
    0x070CA959: "NetworkSessionManagerLive",
    0x070E12F8: "TypeDescriptor",
    0x070E7278: "ID3DXSprite",
    0x070FD915: "BIU_PERFCOUNTER3_HI",
    0x0716D0FB: "sGpuParticle::Context::__vftable",
    0x0718B585: "NetworkXboxMediator",
    0x071AD96C: "tagColorConvertStatus",
    0x071C0009: "_XCONTENT_DOWNLOAD_GET_INPROGRESS_METADATA",
    0x071E345A: "FSB_TLA_TRACE_ARRAY_DATA0",
    0x071E63F2: "MC0_WR_STR_DLL_0",
    0x071EAC1C: "SCRATCH_REG0",
    0x071F55A9: "MtSize",
    0x0721F14B: "cEmc2ActDown",  # pc-only
    0x07240029: "FSB_LX_DEBUG_AUX",
    0x072A0F05: "uEffect2D::GEN_RNO_TBL",
    0x072DF97A: "cAIPositionEvaluationFunc",  # pc-only
    0x07307FA9: "MtMemoryStream::__vftable",
    0x07347DD0: "_XINPUT_VIBRATION",
    0x0738FA28: "rEffectAnimation",
    0x073A39FB: "FSB_TLA_DEBUG_BUS_CTRL",
    0x073A4FA5: "XAUDIO::CWaveFileWriter::__vftable",
    0x0741BC74: "_XMUICO4",
    0x07437CCE: "rSoundAttributeSe",  # pc-only
    0x07480A64: "TP0_PERFCOUNTER1_SELECT",
    0x074C0C0C: "_P_QUERY_AFFILIATES_REPLY_MSG",
    0x07525F56: "FSB_LX_ERRCAP",
    0x0753AB02: "cEm83ActTurn",  # pc-only
    0x0756EF54: "SQ_CF_LOOP",
    0x075DCA29: "cEm84PlEvent_StripEnd",  # pc-only
    0x0760F882: "VGT_VERTEX_REUSE_BLOCK_CNTL",
    0x07634B91: "cEm41ActFarCatchEscape_PL",  # pc-only
    0x07644537: "MC0_TIMING_CNTL_1",
    0x0767771C: "cAIWorldInterfaceOutputModule",  # pc-only
    0x0767CD2B: "cAIFSMManager",  # pc-only
    0x0769F4D5: "MtCollada::__vftable",
    0x076E78A8: "cPlAction_pl_act_gunemp_ride_on",  # pc-only
    0x0778BF46: "_XEX_KEY_VAULT_PRIVILEGES",
    0x07797B1E: "cEm40ActFarPull",  # pc-only
    0x077FE42C: "_XOTSKERBINFO",
    0x07818CE7: "cAIPositionPickUpObjectWork",  # pc-only
    0x07818EC0: "uBioFilter",  # pc-only
    0x078B7CEE: "GPUCLIPPLANEMODE",
    0x078F4678: "_DXVA_Status_VC1",
    0x0791C1FD: "_DVD_XGD2_DISC_AUTH_RESULT_AUTH_PAGE_HEADER",
    0x0792226E: "D3D::LoopPart",
    0x0792998A: "VResult",
    0x0797780F: "NetworkPeerParamMultipleUdp",
    0x07993618: "_P_PRESENCE_SUBSCRIBE_MSG",
    0x0799DD8E: "uEffect2D::MyDTI",
    0x079E1527: "_s_CatchableTypeArray",
    0x07A1A236: "_CMVScale",
    0x07A247E4: "_RUNTIME_FUNCTION",
    0x07AB4950: "PatInterface::CircleInfo",
    0x07ABFA7A: "GC_REVISION_ID",
    0x07ADBA8A: "cEm32TongueActWait",  # pc-only
    0x07B13EB9: "cPlAction_pl_act_wall_crouch_turn_l",  # pc-only
    0x07B439BD: "CP_RB_WPTR_DELAY",
    0x07B71C36: "DC_LUT_RW_MODE",
    0x07B77A14: "MtCollada::Combiner",
    0x07B8BCDE: "rFacialAnimation",
    0x07BBFDE9: "ID3DXSkinInfo",
    0x07BFF10E: "_XMARKETPLACE_QUERY_PARAMS",
    0x07C35F3E: "XUIAllocatedArray",
    0x07C4E6FD: "DC_TEST_DEBUG_DATA_TRIGGER_MASK",
    0x07C5AA65: "CP_RT6_SIZE",
    0x07C95FDF: "CP_RT3_POLL_ADDRESS",
    0x07CDFD0E: "CP_RT11_REFERENCE",
    0x07D2FC6E: "cFSMOrderPawn::cMotionAct",  # pc-only
    0x07D496D4: "sLightLinker::uSphere",  # pc-only
    0x07D59D66: "cPlAction_pl_act_damage_ice_vs",  # pc-only
    0x07D647F2: "SB_DEVICE_ID",
    0x07D7E97B: "_D3DXSHADER_COMPILE_PARAMETERSW",
    0x07D8C3A0: "FSB_LX_PMC1_OR",
    0x07D9317E: "_D3DXPARAMETER_DESC",
    0x07DAB90D: "_STFC_FCB_BASE",
    0x07DB6C60: "_PixCCVideoOp",
    0x07DB8506: "D1GRPH_COLOR_MATRIX_COEF_2_4",
    0x07DC24D9: "NetworkSessionStable::RelayRoute",
    0x07DE52AE: "in_addr",
    0x07DED598: "ID3DXKeyframedAnimationSet::__vftable",
    0x07E082C7: "_KUSER_MODE_TYPE",
    0x07E43FF0: "rEffectSetData::ESD_LIFE_FRAME",
    0x07E58A20: "strHeaderInfo_WMC",
    0x07E64F37: "XUIRenderInitParams",
    0x07F09CE5: "_VD_VIDEO_MODE_INFO",
    0x07FB0C0D: "HACCEL__",
    0x0800D55B: "cEm10ActDmgGGHead",  # pc-only
    0x080A55DA: "NetworkRankingLive::moveGetRankingAttach::__l3",
    0x080E1DDF: "_CEA861_SHORT_AUDIO_DESCRIPTOR",
    0x081222EC: "rVibration::VIB_INDEX",
    0x0813FD63: "uEffectVFR::GEN_STATUS",
    0x081BA411: "_DVD_XGD2_DISC_AUTH_RESULT_HV_MARSHAL",
    0x081D43F6: "IOC_HARD_RESET",
    0x081E0881: "uOm0941::cAction_wait",  # pc-only
    0x08227C6A: "PIX_REQUEST_TIMING_CAPTURE",
    0x082319F0: "CRTC_DEBUG_ID",
    0x0825A2DB: "_XAMACCOUNTINFO",
    0x0828DF8E: "cScenarioArg_Message",  # pc-only
    0x083084AB: "_MAX_FVF_DECL_SIZE",
    0x083193D9: "DCCG_ONE_SHOT_STOP_CLOCKS_CNTL",
    0x08419E49: "_D3DXFRAME",
    0x084733AB: "_FILE_TRACKING_INFORMATION",
    0x084F4D2C: "uOmCoopTreasure::cActPlBase",  # pc-only
    0x08502F97: "cEm34ActJump",  # pc-only
    0x08509BE2: "D1MODE_LB_PITCH_IN_WORDS",
    0x0850CC72: "uOmClutch::cActDown",  # pc-only
    0x0855DC2E: "CODECGETDEPSTREAMCONTEXT",
    0x08578F46: "sSoundN::StreamVoice::FADE_STATUS",
    0x0858D598: "cOpeEmotion",  # pc-only
    0x08661BB8: "uOmGlass::cActWait",  # pc-only
    0x08669B06: "CCalMovieDecoder",
    0x086BC45F: "CP_IB1_BASE",
    0x0873A1A3: "PCIE_PERF_LATENCY_COUNTER1",
    0x0876344C: "_HDCP_NOTIFICATION_REGISTRATION",
    0x087A15EB: "MC0_DRAM_CMD",
    0x087CE594: "cTrans::TextureBase::__vftable",
    0x087D1F86: "uOm0927_Crane::cActWait3",  # pc-only
    0x088063A3: "cEm22ActAtkCut",  # pc-only
    0x088196FD: "tagFrameDecPath",
    0x0886633E: "XAUDIOREVERBSETTINGS",
    0x08881E25: "uModel::RenderInfo::RENDER_MODE",
    0x088A6868: "BIOS_10_SCRATCH",
    0x088B7238: "_XSTORAGE_ACCESS_TOKEN",
    0x088CAD55: "CP_PERFCOUNTER_HI",
    0x08933612: "XML_ELEMENT_DEFINITION",
    0x08972FAD: "DMIF_DEBUG_ID",
    0x089818AE: "AUDIORENDERINGSETTINGS",
    0x0898558A: "CBitStream",
    0x089E00E4: "tagSTGTY",
    0x08A0B417: "XAUDIO::CObjectRefCount",
    0x08A57A0C: "XHTTP_ASYNC_RESULT",
    0x08A7966E: "cNetEm10",  # pc-only
    0x08B09AE7: "D1CRTC_STATUS_POSITION",
    0x08B55184: "sSoundN::DISTANCE_CURVE_TYPE",
    0x08B69550: "cEm0bActWalk",  # pc-only
    0x08B87D21: "MtFrustum::PLANE_TYPE",
    0x08B92C49: "PA_SC_PERFCOUNTER0_SELECT",
    0x08B937D1: "rMovieOnDisk::MyDTI",
    0x08BA54F7: "FSB_LX_PMC5_OR",
    0x08BE500A: "CP_PERFCOUNTER_SELECT",
    0x08C18985: "uEffectVFR::Generator",
    0x08C429C4: "_XMATCH_SEARCH_REQUEST",
    0x08C88617: "uActorModel::EffectEmitter::END_TYPE",
    0x08CE75A8: "cEm10ActWalk",  # pc-only
    0x08CF1DBF: "sTool::OP_MODE",
    0x08D5E462: "uEffectEdit::MoveNone",
    0x08D62270: "XCOMPRESS::decoder_state",
    0x08D8972A: "cAIModuleList::Layer",  # pc-only
    0x08DE697B: "TCF_PERFCOUNTER8_HI",
    0x08E3F7CD: "rEffectSetData::ESD_SET_POLYGON",
    0x08E72564: "cAIAStar::AStarNode",  # pc-only
    0x08E84E11: "sShader::LIGHTING",
    0x08E9200C: "cEm66ActAtkRaftBite",  # pc-only
    0x08EB563C: "CP_ME_RT_ADDR",
    0x08EF0854: "rSoundDirectionalSetXml::Curve::MyDTI",
    0x08F1D48C: "XUIMessageItemCheck",
    0x08F26F9B: "MC1_SECURE_MEMORY_APERTURE_SIZE",
    0x08F4A2F6: "_UCODE_PASS_HEADER",
    0x08F6F510: "cEm0bActDmgS",  # pc-only
    0x08FBD28D: "_XACTIVATION_GET_TITLE_LIST_RESPONSE",
    0x08FC6ED9: "RB_COLOR2_INFO",
    0x08FD5464: "_CEA861_SHORT_VIDEO_DESCRIPTOR",
    0x0903E9BC: "_XMARKETPLACE_ASSET",
    0x09052149: "MtDataWriter::Label",
    0x09081E7E: "cAIAStar_Share",  # pc-only
    0x0908E7F5: "cFSMOrder::FuncParamF32",  # pc-only
    0x090C8CBF: "_XMDECN4",
    0x090E9913: "_XSESSION_LOCAL_DETAILS",
    0x0910E4BD: "cEm84PlEvent_Pinion",  # pc-only
    0x09198190: "cUnit::UNIT_ATTR",
    0x0919B72D: "cTrans::VertexBuffer::MyDTI",
    0x091C5477: "rHavokVertexLayout",  # pc-only
    0x091E2002: "cAIWorldInterfaceModule",  # pc-only
    0x09204585: "uOmLaserMirror::cActWait",  # pc-only
    0x092AC966: "HdrDecodeStatus",
    0x092AFA9E: "_GRAPHICS_COLOR_ADJUSTMENT",
    0x092B2427: "_STFC_DIRECTORY_LOOKUP",
    0x092C85A2: "XUIMessageMouse",
    0x092D4227: "CP_RB_CNTL",
    0x092EE2F8: "CP_RT2_REFERENCE",
    0x09316F04: "cPlAction_pl_act_coop_jump_broad_6m_jump",  # pc-only
    0x09319A33: "MtGeomTriangle",
    0x0931D289: "uOmSwitch3::cActPullLoop",  # pc-only
    0x0937A8C7: "_KTIMER",
    0x093CE570: "rLotSelectorMoveXml",  # pc-only
    0x093F48D4: "_XOKERBINFO",
    0x094538B6: "_D3DXSHMATERIAL",
    0x094569CE: "NetworkLayer::NameList",
    0x09491C0B: "rEffectList::ADHESION_OPTION_FLAG",
    0x0949BD3A: "PG_SIZE",
    0x094A3A97: "rMovieOnDiskInterMediate::MyDTI",
    0x094D560E: "cOmCoopTwistActWait",  # pc-only
    0x094E1A14: "_MarkerEntry",
    0x094E59E3: "_CondR",
    0x0950FD86: "uOm08ac_Fence::cActWait",  # pc-only
    0x09526305: "cEm71ActDie",  # pc-only
    0x095264F7: "rModel::MATERIAL_INFO",
    0x0958AE18: "cEm65ActDieIce",  # pc-only
    0x095D412E: "VGT_LAST_COPY_STATE",
    0x096E7247: "XAUDIO::XAUDIOSRCPRIVATE",
    0x0971C600: "SQ_FETCH_1",
    0x097A10C1: "_XWMDRM_CERTIFICATE_BLOCK",
    0x097A1A9E: "AZ1_MRU_BANK10_DEPTH_MASK",
    0x097D5A16: "uToneMapFilter::TMSTAT",
    0x097ECC05: "PatInterface::MailHead",
    0x097EF167: "_XMSG_ENUM_RESULTS",
    0x097F10F0: "CXuiImageElement",
    0x098154AA: "uOmS508_Break::cActBreak",  # pc-only
    0x0985C00A: "cOmCoopGateActionPl",  # pc-only
    0x0985E45C: "_DXVA_SampleFormat",
    0x098CDB77: "_XMUSHORTN4",
    0x098F9F83: "rEffectSetData::FILTER_OPTION_FLAG",
    0x0992D958: "cEm40ActRegene",  # pc-only
    0x09937705: "_STFC_WORKER_THREAD_CONTEXT",
    0x09A13CD9: "IXUIPropObj",
    0x09A1B762: "cEm10ActAtkSitGunShot",  # pc-only
    0x09A71FA1: "CCalImageMetadata",
    0x09AAE100: "rConfig::ITEM",
    0x09AC9215: "STREAMINDEXEDDATA",
    0x09ACBC25: "AZ0_MRU_BANK11_DEPTH_MASK",
    0x09AF9AAE: "REMOTETALKER",
    0x09B5EC5A: "AZ0_LOOPBACK_PATTERN2PHS0",
    0x09B7AA35: "XMAPACKETPOSITION",
    0x09B7DD40: "cAIFlockFinder::NeighborInfo",  # pc-only
    0x09C08276: "cEm10ActAtkGunBombPeepR",  # pc-only
    0x09C2B03D: "rSoundDirectionalCurveXml::TargetPlatform",
    0x09C40D96: "rArchive::CompressStream",
    0x09C52A21: "_PASSPORT_CHANGE_WINDOWS_LIVE_ID_REQUEST",
    0x09C5628D: "SubFrmDecodeStatus",
    0x09CB8ACF: "rSoundRequestXml",
    0x09CF293F: "_FILE_POSITION_INFORMATION",
    0x09D0E5FE: "IDirectXFileSaveObject::__vftable",
    0x09DB0010: "sResource::ASYNC_PRIORITY",
    0x09DDAAAA: "cOmCoinAction",  # pc-only
    0x09E15313: "cEmc0ActShift",  # pc-only
    0x09E337C8: "cEm84ActProvoke",  # pc-only
    0x09E8FC85: "uOmJeep::cActWepBase",  # pc-only
    0x09E9F4D1: "std::locale::facet::__vftable",
    0x09EB71D0: "uOm0927_Crane::cActMoveAB",  # pc-only
    0x09ED06F6: "rEffectSetData::ESD_SET_MODEL_COMMON",
    0x09EE2245: "MtCollada::Scale::MyDTI",
    0x09EF94AF: "ID3DXLine::__vftable",
    0x09F080E7: "_FILTER",
    0x09F63949: "cMotVarManager",  # pc-only
    0x09FE3F91: "CP_RT5_MASK",
    0x09FE7917: "cEm65ActTurn",  # pc-only
    0x0A00DC0E: "FSB_TX_TERST_AND",
    0x0A01EEFA: "XAUDIO::CEffect",
    0x0A0A1DA1: "cTrans::MESH",
    0x0A0AF139: "XAUDIO::CVoice",
    0x0A0BAA4B: "cOmCoopCardDoorActClose",  # pc-only
    0x0A115161: "D3D::ParseLookup",
    0x0A152EDA: "METADATADESCRECORDS",
    0x0A153F3B: "PIX_REQUEST_MOVIE_PLAYBACK",
    0x0A18546B: "MC1_INTERRUPT_ACK",
    0x0A1B21C9: "_PixGroupsType",
    0x0A1F2936: "CWMVMBMode",
    0x0A22A8A3: "CSchemaData",
    0x0A232AFE: "uOmLoadItem::cActItemLoad",  # pc-only
    0x0A2813FE: "XONLINE_FRIEND_LIST_INTERNAL",
    0x0A29BF26: "aS200::cActEvPlBoatAirRideOff",  # pc-only
    0x0A2BDFF7: "DO_TEST_DEBUG_OUT_TEST_DATA",
    0x0A3411A7: "cEm0cActStep",  # pc-only
    0x0A39D6F1: "_IMAGE_VXD_HEADER",
    0x0A3ACB73: "FSB_LX_PMC3",
    0x0A3C4660: "uOmJeep::cActPlActBtn",  # pc-only
    0x0A3D1E38: "_STRING64",
    0x0A3EBEBA: "_HARDWARE_PTE",
    0x0A41BBCF: "AZ0_RESET_LOOPBACK_TRANSMIT_LFSR",
    0x0A49ECA5: "_SUITE_TYPE",
    0x0A576AC3: "cEm66ActDieWater",  # pc-only
    0x0A57D7BB: "sNetwork",
    0x0A5CEBBA: "_D3DCAPS9",
    0x0A5F09F3: "_XENUMERATORASSET",
    0x0A63131C: "XAUDIOSOURCEBUFFER",
    0x0A6416CF: "_VideoInterlaceMetaData",
    0x0A656F19: "cEm42CActBlow",  # pc-only
    0x0A6647CF: "sRender::MSAA",
    0x0A69EF7E: "XMASTREAMFORMAT",
    0x0A6B1452: "uEffect2D::PTCL_FLAG",
    0x0A6DE7EF: "cOmBoatAirAction_pl_act_ride_on",  # pc-only
    0x0A78FF01: "XAUDIO::XMAPacketHeader",
    0x0A7A4478: "CXLiveOffering",
    0x0A7C184A: "RB_COPY_DEST_INFO",
    0x0A7C21E1: "AZ1_MRU_BANK14_DEPTH_MASK",
    0x0A808A30: "cMaterialStandard::FUNC_MULTITEXTURE",
    0x0A813338: "cEm60ActRun",  # pc-only
    0x0A8541B7: "uProjectionEffect",
    0x0A86AC80: "tagWMCExtendedContentDescription",
    0x0A86FD2A: "REG_MACRO_ADDR_3",
    0x0A88884F: "_MESSAGE_RESOURCE_BLOCK",
    0x0A8C8A80: "cEm30ActDmgGetup",  # pc-only
    0x0A8CD06B: "D1SCL_UNDERFLOW_STATUS",
    0x0A985CC4: "MtCollisionTree::Node::__vftable",
    0x0AA0213D: "_XE_CONSOLE_SIGNATURE",
    0x0AA0FC4C: "cEm0bActDieInvalid",  # pc-only
    0x0AA4F157: "cEm0bActDmgBlown",  # pc-only
    0x0AA5DD61: "XSVLTCACHE",
    0x0AA83FB2: "sBioShader",  # pc-only
    0x0AA86CBE: "_XPRESENCE_SYNC_SUB_RESULT",
    0x0AAA875A: "AZ0_MRU_BANK15_DEPTH_MASK",
    0x0AAB1E9E: "UVCHANNELINFO",
    0x0AAF5B5F: "_Chex",
    0x0AB325AB: "cEm65ActWaitAttack",  # pc-only
    0x0AB34DC8: "DCCG_TEST_CLK_SEL",
    0x0AB389D5: "AZ0_SECONDARY_STATE_DWORD4",
    0x0AB5311E: "_FIND_USERS_RESPONSE",
    0x0AB5B3E8: "uEffectVFR::Model::TEX_SCROLL_FLAG",
    0x0AB6228C: "ChXformStatus",
    0x0AB8E575: "PA_CL_VPORT_ZOFFSET",
    0x0ABA3C3F: "cEm3402ActErase",  # pc-only
    0x0ABB2376: "MC0_DRAM_CONFIG",
    0x0AC6749C: "NetworkRankingLive::moveGetRankingScoreListByRange::__l3",
    0x0AC8D992: "cPlAction_pl_act_back",  # pc-only
    0x0ACCE562: "XAUDIO::XMAPLAYBACKSTREAM",
    0x0ACDF089: "uFreeCamera::MyDTI",
    0x0AD7F504: "RB_BC_AZ1_CRC",
    0x0AD890DA: "_XDVRSTORAGE_ALLOCATE_PARAMS",
    0x0ADE4840: "uBlurFilter::BLUR_TYPE",
    0x0ADE818D: "uEffect2D::MoveMul",
    0x0ADF37B1: "XDVO_2ND_CRC_EN",
    0x0AEA8C47: "NetworkSocket",
    0x0AEB6158: "cTrans::TextureBase::ENCODE_TYPE",
    0x0AEBB7D5: "_XCONFIG_SECURED_ENTRIES",
    0x0AF31194: "cEmc0ActErase",  # pc-only
    0x0AF4EA19: "_XCONTENT_REFERRAL_REQUEST",
    0x0AF8E740: "cEm32ActDmgFallCeil",  # pc-only
    0x0AFA4A28: "COMPLETIONINFO",
    0x0AFAF248: "cAIFSM::ParamArrayProperty",  # pc-only
    0x0AFE4E0C: "rEffectList::CULLING_FLAG",
    0x0B00ADFA: "D3D::CMicrocodeBuilder::StreamWriter::State",
    0x0B03D37A: "_PredictMVLUT",
    0x0B0B2852: "cEm32TongueAction",  # pc-only
    0x0B0C8FCF: "CFFILE",
    0x0B12951B: "TCF_PERFCOUNTER3_SELECT",
    0x0B12B6E7: "_XUSAGE_STORE_RESULT",
    0x0B13B381: "RTS_I_W_REF",
    0x0B15C795: "cEm32ActDmgBlown",  # pc-only
    0x0B170D2A: "cPlAction_pl_act_attack_combo_straight",  # pc-only
    0x0B1AAA6B: "cOmCoopGateAction_pl_act_ready",  # pc-only
    0x0B1D65D9: "FSB_TX_PMC0_OR",
    0x0B246C7C: "tagWMCDateParams",
    0x0B2A46F4: "_audecGetPCMParams",
    0x0B2FCDCE: "DM_XAM_SERVICES",
    0x0B35A10B: "cOmBoltActOpen",  # pc-only
    0x0B3C8C6A: "XUINotify",
    0x0B434DBC: "_DXVA_ConfigAlphaLoad",
    0x0B450FCB: "HKEY__",
    0x0B457DEE: "cPlAction_pl_act_knife_ready_begin",  # pc-only
    0x0B4A2CD7: "cEm32ActGroundToCeil",  # pc-only
    0x0B4B4CE7: "MtHeapArray",
    0x0B4E5DF7: "uShadow::LEGACY_PCF_FILTER",
    0x0B5184F6: "cEm30ActDmgDieFreeze",  # pc-only
    0x0B556924: "sPrim::Material::AttributeType",
    0x0B5B366D: "HSIO_CALIBRATE",
    0x0B627EA0: "NetworkRanking::Updater",
    0x0B637D19: "uOmS104_Driver::cActBase",  # pc-only
    0x0B6727D9: "PCIE_RX_TLP_CRC",
    0x0B674970: "FSB_TX_TERSTM_OR",
    0x0B6A8A1C: "PCIE_PERF_COUNT0_TXCLK",
    0x0B6BD303: "PatInterface::CirclePassword",
    0x0B6D1DC7: "cEm40ActSSURegene",  # pc-only
    0x0B75A1EA: "cEm32ActGetup",  # pc-only
    0x0B7A163B: "_AUDIT_EVENT_TYPE",
    0x0B7EC876: "sVibration::VibControl::ENABLE_FLAG",
    0x0B7FFE76: "std::length_error",
    0x0B805E2A: "uOmSpileTrap::cActBoot",  # pc-only
    0x0B822975: "MtRegistry",
    0x0B82D558: "cEm52Action",  # pc-only
    0x0B8530E2: "MtHalf",
    0x0B871058: "_XSTORAGE_DELETE_REQUEST",
    0x0B8817AA: "SB_BASE_CODE",
    0x0B89323C: "cEm30ActTurn",  # pc-only
    0x0B89BA6E: "_PIX_AUTOMATION_MESSAGE",
    0x0B8EAA32: "cAIGraph::Node",  # pc-only
    0x0B961CC1: "D1CRTC_STEREO_STATUS",
    0x0B96ECF2: "AZ1_SECONDARY_STATE_DWORD4",
    0x0B9EB128: "CHuffmanTable::huffmantab",
    0x0BA0FEA8: "D3DXVECTOR2",
    0x0BA12AC2: "MP4SLConfigSettingsRecord",
    0x0BABF592: "cEm70ActWait",  # pc-only
    0x0BAFC9CF: "_PIXSHAREDCAPTUREINFO",
    0x0BB1F1C5: "IXAudioBatchAllocator",
    0x0BB65DC4: "rSoundSpeakerSetXml::Speaker",
    0x0BB8A401: "TEST_COUNT_CNTL",
    0x0BB8A614: "uScreenMap::MyDTI",
    0x0BB8DC90: "IXAudioSourceEffect::__vftable",
    0x0BB96C33: "NB_STATUS",
    0x0BBA6F3D: "IDirectXFile",
    0x0BBF1BCD: "_CACHE_PARTITION_DATA",
    0x0BC1ACE0: "SXIFCCG_DEBUG_REG1",
    0x0BC36131: "cLinkUnit::cTargetEnemy",  # pc-only
    0x0BCDE3C5: "_NOTIFICATION_UPDATE_STATE_FLAGS",
    0x0BCE8A60: "PA_SC_DEBUG_CW_0",
    0x0BCF5734: "AZ1_LOOPBACK_PATTERN2PHS3",
    0x0BD1153D: "NetworkSession::Voice",
    0x0BDB5735: "XG_MCT::SimpleCode",
    0x0BDC89B6: "TSRESULT",
    0x0BDF50B8: "cEm3401ActOut",  # pc-only
    0x0BE06B3F: "_XUSER_ESTIMATE_RANK_REQUEST",
    0x0BE08C53: "rClothXml::Index::MyDTI",
    0x0BE22041: "_RTL_TIME_ZONE_INFORMATION",
    0x0BE3464E: "_RESTRICTED_PRIVILEGE_BIT",
    0x0BE496DC: "_CACHEHASHTABLEITERATOR",
    0x0BF0D16A: "_FXLRENDERSTATE",
    0x0BFC142B: "cLinkUnitFSM::cScenarioArg_SetFSM",  # pc-only
    0x0BFCE58A: "uAdhesion::FUNC_ADHESION_MASK_TYPE",
    0x0C03A733: "cTrans::HDR_MODE",
    0x0C064075: "sCollision::ScrColInfoAdjustPosition::MyDTI",
    0x0C07D75A: "FSB_LX_DEBUG_HI",
    0x0C0D39B2: "MtDataReader::__vftable",
    0x0C0D99BB: "uEm34::cEm34ActPlBase",  # pc-only
    0x0C113F40: "rScheduler::KEY",
    0x0C14C152: "PIX_STREAM_VIDEO_COST",
    0x0C14D9A5: "uFilter::MyDTI",
    0x0C150DD7: "cOm08baEventPL_ActFall",  # pc-only
    0x0C189E0A: "rSoundRandom::MyDTI",
    0x0C199B37: "RTS_EDGE_1_DX",
    0x0C19D386: "MtProperty::TYPE",
    0x0C1A216D: "cEm30ActJump",  # pc-only
    0x0C1C0753: "IOC_INT_CONTROL",
    0x0C1D0302: "ID3DXFileSaveObjectVtbl",
    0x0C1F10BE: "sGpuParticle::MyDTI",
    0x0C2401C6: "tagPOINT",
    0x0C261A1D: "cEm22ActDieBomb",  # pc-only
    0x0C27AF46: "NellyAGC_mblk",
    0x0C2EE9AF: "cJointCombi",  # pc-only
    0x0C316373: "_XSTORAGE_FILE_INFO",
    0x0C32D24D: "XAUDIOPACKET",
    0x0C344372: "NetworkIpAddress",
    0x0C3A6AC5: "sCollision::Node::MyDTI",
    0x0C3FD9B7: "sCollision::CallbackInfo",
    0x0C41EAAA: "_TOKEN_CONTROL",
    0x0C499F39: "_DISPATCHER_CONTEXT",
    0x0C49A4A2: "std::runtime_error",
    0x0C504C1C: "CP_RB_BASE",
    0x0C55BAC0: "uOm0892_Lift::cActMove",  # pc-only
    0x0C562B41: "D3D::CMicrocodeBuilder::D3DFastVector",
    0x0C60069A: "_GET_ACCOUNT_INFO_REQUEST",
    0x0C606D06: "_XPRESENCE_SYNC_SUBS_REQUEST",
    0x0C60F961: "rEffectList::EFL_GENERATOR",
    0x0C627021: "LOOPBACK_EXTENSION",
    0x0C66B279: "XGI_SESSIONREGISTER_MSG",
    0x0C689273: "XNADDR",
    0x0C6BD775: "cEm41ActFarCatch_PL",  # pc-only
    0x0C6C7C85: "sRender::Pass::COUNTER_TYPE",
    0x0C6DAA48: "cTrans::IndexBuffer",
    0x0C6F58B2: "JBPACKET",
    0x0C7202BC: "cPlAction_pl_act_die_lie",  # pc-only
    0x0C721ACE: "_P_ADD_2_MSG_INTERNAL",
    0x0C73E21F: "tCVector_X9",
    0x0C74E157: "PatInterface::LogInfo",
    0x0C767B54: "CP_RB_RPTR_ADDR",
    0x0C786E75: "cEm83ActAppear",  # pc-only
    0x0C795688: "_PASSPORT_CHANGE_PASSWORD_REQUEST",
    0x0C79904D: "cPlAction_pl_act_wall_crouch_t_ready",  # pc-only
    0x0C7DE2E0: "PCIE_LC_LINK_WIDTH_CNTL",
    0x0C81B5B3: "XUIMessageGetSoundState",
    0x0C893274: "_DXVA_AYUVsample2",
    0x0C966F55: "CXContentDownload::REFERRAL_RESPONSE_BUFFER",
    0x0C9C6626: "cEm10ActDeadFaceDown",  # pc-only
    0x0C9CD3DF: "cTurbo",  # pc-only
    0x0C9D980D: "MC0_PERFCOUNTER0_LOW",
    0x0CA64492: "cEm41ActDiscloseRegene",  # pc-only
    0x0CA9F425: "FSB_LX_PMC2_AND",
    0x0CB0C28B: "CXStorageMiscParent::__vftable",
    0x0CB1A8A4: "DECODERSTATE",
    0x0CB61C46: "MC0_TERM_CNTL",
    0x0CB7979F: "uTextureBlend::CUBIC_VERTEX",
    0x0CBDF114: "GPUSYNCFUNCTION",
    0x0CC71B5C: "METADATAPERSTREAM",
    0x0CC882E0: "tagWMVPostLevel",
    0x0CC8C6D4: "rEffectList::CHAIN_OPTION_FLAG",
    0x0CCAAB2F: "VC_ENHANCE",
    0x0CCB44E8: "SSID_ID",
    0x0CD03FAC: "cEm65ActGoWalk",  # pc-only
    0x0CD54E7C: "cOmCoopDoorAction_pl_act_push_ready",  # pc-only
    0x0CD66598: "_P_FRIENDS_LIST_REPLY_MSG",
    0x0CD86EB8: "uLight::MyDTI",
    0x0CD9D2FB: "ID3DXSkinInfo::__vftable",
    0x0CDD0440: "cOmContainerAction_waitUp",  # pc-only
    0x0CDEDE04: "_XMSG_DELETE_REQUEST",
    0x0CE04EF9: "MC0_PAD_IF_CNTL",
    0x0CE0DEAF: "cEm66ActAtkSwimBiteHit_PL",  # pc-only
    0x0CE194B7: "ID3DXInclude::__vftable",
    0x0CE91E3C: "BIU_PERFCOUNTER2_SELECT",
    0x0CEAAAB3: "cPlAction_pl_act_attack_reverse_knuckle",  # pc-only
    0x0CEB104F: "CP_RT8_BADR",
    0x0CED0A50: "sCollision::ScrColInfoCastConvex::MyDTI",
    0x0CFB28EB: "AZ1_SECONDARY_STATE_DWORD0",
    0x0CFD5446: "_XUSER_ADDPLAYER_MSG",
    0x0CFED18C: "cAIPacketQueue",  # pc-only
    0x0D0B0E6D: "_OBJECT_HEADER_NAME_INFO",
    0x0D0D44FE: "uSynchroSpotLight",
    0x0D104EEE: "cOmDoorAction",  # pc-only
    0x0D155326: "XMicrocodeBuilder",
    0x0D159162: "_CACHEFILETABLEENTRY",
    0x0D174DE5: "sSoundN::EQ_CATEGORY",
    0x0D179D55: "_XMSG_CREATE_REQUEST",
    0x0D1A697F: "cPlAction_pl_act_avoid_back",  # pc-only
    0x0D1C0BCE: "D3D::EnumDescription",
    0x0D230BAE: "_HDD_SECURITY_BLOB",
    0x0D23FA1B: "TCF_PERFCOUNTER10_LOW",
    0x0D24D2CC: "XAUDIO::CPacketQueue",
    0x0D2F1B69: "cShape::MyDTI",
    0x0D2FEF94: "cOmBoatAirAction_om_act_damage",  # pc-only
    0x0D3037C4: "_XVIRTUALKBDUI_PARAMS",
    0x0D309B2B: "FSB_TX_DEBUG_AUX",
    0x0D3353F0: "uBioShadow",  # pc-only
    0x0D37517B: "PCIE_P_PORT_LANE_STATUS",
    0x0D3AEC49: "D3DXShader::CNode",
    0x0D3D0760: "XCOMPRESS::LZXCONFIGURATION",
    0x0D3FC1C4: "CP_RB_RPTR",
    0x0D41338B: "XAUDIO::CThread",
    0x0D4653DB: "_RTL_HEAP_TAG_INFO",
    0x0D4A37B8: "FSB_LX_DADD_OR",
    0x0D4C255D: "uIdAlert00",  # pc-only
    0x0D4F93D3: "D3D::CMicrocodeBuilder::DefinitionTable",
    0x0D50246F: "uOma004_Collapse::cActPlFailed",  # pc-only
    0x0D5A2C82: "cEm10ActAtkTorchDash",  # pc-only
    0x0D5CA6DC: "PRESENCE_CONTEXT",
    0x0D60B38C: "_XCPT_ACTION",
    0x0D62DD72: "_XONLINE_TEAM",
    0x0D6354F7: "uOmTreasureBox::cActOpen",  # pc-only
    0x0D6667FB: "cEm10ActDeadNormalPF",  # pc-only
    0x0D67B7E0: "MP3SCF",
    0x0D6AF6C7: "_XPROFILE_ENUM_ACHIEVEMENTS_REQUEST",
    0x0D70FF71: "SQ_FETCH_RT_2",
    0x0D766BD9: "D1OVL_SURFACE_OFFSET_Y",
    0x0D7868EE: "princeton_digital::vardelay_t",
    0x0D7C9D85: "uOmCrank::cActPlOrder",  # pc-only
    0x0D7EA974: "sCubeMapInterp",  # pc-only
    0x0D856463: "cDemoStartUp",  # pc-only
    0x0D86304B: "_XNET_LOGON_DNS_TYPE",
    0x0D8838FF: "BIU_TOP_OF_MEM",
    0x0D8D81B0: "_OFFER_PURCHASE_GAMERTAG_REQUEST",
    0x0D9119BE: "cEm40ActFarEscape",  # pc-only
    0x0D916597: "_PredictMVLUT_UNION_MISC",
    0x0D952B3F: "cEm40ActCollectEscape",  # pc-only
    0x0D96A21B: "cEm84ActTurn",  # pc-only
    0x0D9C7AFE: "tCMVPred",
    0x0D9D7C31: "sVibration::VibControl::__vftable",
    0x0DA08E27: "_WIN32_FIND_DATAA",
    0x0DA5684E: "_IMAGE_SECTION_HEADER",
    0x0DA85C53: "cAITerrainVisibilityAnalyzer",  # pc-only
    0x0DACA7BA: "MtSH",
    0x0DADAB62: "rObjAdj",  # pc-only
    0x0DAF031D: "_OBJECT_NAME_INFORMATION",
    0x0DB296BD: "cFSMOrder::FuncParamJumpArea",  # pc-only
    0x0DB33743: "NetworkRanking::Score",
    0x0DB3EADE: "_DXVA_VideoDesc",
    0x0DBF592D: "cEm40PActSleep",  # pc-only
    0x0DBF733D: "MtCollada::Controller",
    0x0DC2B5A3: "_IMAGE_RESOURCE_DIRECTORY_ENTRY",
    0x0DC331F8: "rEffectList::EFL_PARTICLE_LENS_FLARE",
    0x0DC4A9A1: "XUIMessageParentChanged",
    0x0DCAFC6B: "cEm8eDmgPinionAct",  # pc-only
    0x0DCB996D: "cArea::MyDTI",
    0x0DD06053: "_XEX_IMPORT_DESCRIPTOR",
    0x0DD31DDC: "uMotionCameraNoise",  # pc-only
    0x0DD3C2A8: "CP_NV_FLAGS_2",
    0x0DD419EC: "_DXVA_COPPStatusHDCPKeyData",
    0x0DD53842: "cTrans::CubeTexture::MyDTI",
    0x0DD90E8F: "uOmSpileTrap::cActBase",  # pc-only
    0x0DDAAEE3: "_XONLINE_STORE_TYPE",
    0x0DDE4DCC: "AZ0_SECONDARY_STATE_DWORD0",
    0x0DDFAD8F: "cOmContainerAction_liftUp",  # pc-only
    0x0DE3BAF6: "uOm1307_Boat::cActBase",  # pc-only
    0x0DE47CB1: "uPlayer::CALLBACK_CAM_STRUCT",  # pc-only
    0x0DE6F981: "cAITerrainHavokVisibilityAnalyzer",  # pc-only
    0x0DE97119: "_XCOMPRESS_FILE_HEADER",
    0x0DEB3933: "REG_MACRO_ADDR_7",
    0x0DED692D: "rEffectSetData::ESD_SET_FILTER",
    0x0DEE85E6: "cEm10ActAtkPlagaEatStart",  # pc-only
    0x0DF1F6D3: "ID3DXFileSaveData::__vftable",
    0x0DF27444: "_SECURITY_TOKEN_AUDIT_DATA",
    0x0DF75176: "rEffect2D::E2D_KEYFRAME_COMMON",
    0x0DFE654C: "cEmA2ActSyoteEsc_PL",  # pc-only
    0x0E05E61A: "_P_FRIENDS_LIST_MSG",
    0x0E0629CF: "AZ1_RESET_SAMPLE_COUNTERS",
    0x0E06A3C7: "cOmCoopBoxAction_pl_act_ready",  # pc-only
    0x0E08ADE6: "CP_DMA_STAT",
    0x0E098A8A: "cOmDeadAction_fixed",  # pc-only
    0x0E0C3BB9: "RB_HSIO_PHASE_OUT",
    0x0E0DE311: "DNameNode::__vftable",
    0x0E0F1A5B: "uPointShadow",
    0x0E18A25A: "ID3DXConstantTable::__vftable",
    0x0E190907: "CP_ST_BUFSZ",
    0x0E19CC43: "CP_MIU_TAG_STAT1",
    0x0E1C0219: "SQ_FETCH_5",
    0x0E1E5F99: "_D3DXMESHDATATYPE",
    0x0E212D33: "XNetLogonMachineAccount",
    0x0E265AEF: "BIU_PERFCOUNTER0_LOW",
    0x0E284D89: "_s_TryBlockMapEntry",
    0x0E285DAB: "MtSerializer::XmlHandler",
    0x0E2A4D69: "cOmJeepAction_om_act_wait",  # pc-only
    0x0E31C407: "uOmSwitch3::cActPushLoop",  # pc-only
    0x0E324148: "sCollision::__vftable",
    0x0E3B87EC: "cAIPathFinding",  # pc-only
    0x0E3E7BA8: "_TOKEN_GROUPS",
    0x0E46426E: "cWpAction_wp_act_ready_end",  # pc-only
    0x0E4AED13: "RB_COLOR_CLEAR",
    0x0E4F6C2B: "MtCollada::Input",
    0x0E511749: "uOmFollow::cActMove",  # pc-only
    0x0E528085: "tagWMVDimensions",
    0x0E598785: "DC_PERFCOUNTER1_LOW",
    0x0E5AB43D: "_XMSG_DETAILS_RESULTS",
    0x0E5C5713: "_XONLINE_QUERY_ATTRIBUTE_INTEGER",
    0x0E5CC2A1: "uOmS705ceil::cActRise",  # pc-only
    0x0E60B4D6: "cOmDoorEventPL",  # pc-only
    0x0E631AD1: "_D3DBLEND",
    0x0E67EF81: "UVBASE_CONNECTTOVOICECHATPARAM",
    0x0E681C77: "RB_COLOR1_INFO",
    0x0E6ABB39: "ED_CG_CLK_OVERRIDE",
    0x0E6B43A3: "PCIE_RX_CREDITS_RECEIVED",
    0x0E6B4DA4: "uOm1307_Boat::cActMove_C_E",  # pc-only
    0x0E6CE70A: "TP3_CNTL_STATUS",
    0x0E724ED0: "_XIPTV_DVR_QUERY_STATUS",
    0x0E729A04: "MIDILOOP",
    0x0E72ACE7: "LINK_CNTL",
    0x0E784D14: "sShader::VERTEX_FILTER2",
    0x0E784F2E: "cPositionFilterRangeAroundAwayPos",  # pc-only
    0x0E7DF6A0: "_NT_TIB",
    0x0E7E134F: "_ACCESS_DENIED_ACE",
    0x0E7E5D2D: "_PHYSICAL_MEMORY_DESCRIPTOR",
    0x0E7EDA9F: "uEffectVFR::Custom",
    0x0E8053D0: "cPlAction_pl_act_item_get_use_second",  # pc-only
    0x0E8347A6: "GPUEXPORTREGISTER_VS",
    0x0E844BED: "uLevelCorrectFilter",
    0x0E88D70A: "MtCapsule",
    0x0E892204: "cEm40PartsAction",  # pc-only
    0x0E9B9E1B: "XAUDIO::CVoice::__vftable",
    0x0E9D76A8: "_RECTL",
    0x0EA75B08: "cOmBldgAction_wait",  # pc-only
    0x0EAA0263: "tagSTATSTG",
    0x0EAD4A3B: "_LDOUBLE",
    0x0EB21DF6: "RB_BLENDCONTROL0",
    0x0EB22BED: "MtGeomSphere",
    0x0EB419D4: "PIXMetaShaderDebuggerHint",
    0x0EB6B534: "GPUEDRAMMODE",
    0x0EBA0877: "cEm0cActDieBlowFreeze",  # pc-only
    0x0EBC5CF2: "ID3DXFile::__vftable",
    0x0EBF116C: "HSIO_DLL_INIT",
    0x0EC15145: "_XPROFILE_CLEAR_ACHIEVEMENTS_RESULT",
    0x0ECB3DC2: "cEm20ActRun",  # pc-only
    0x0ECBBAA1: "rEffectSetData::ESD_MOVE_PATH_CHAIN_COLL",
    0x0ECD7DF4: "rSoundCurveSet",
    0x0ECDD188: "MtClipboardStream::MyDTI",
    0x0ED2A37B: "_D3DXTECHNIQUE_DESC",
    0x0ED556F6: "MP4ClockReferenceMediaHeaderAtom",
    0x0EE26167: "FRAME_CALL_SETTING_FRAME",
    0x0EE8E2A3: "cPlAction_pl_act_coop_jump_up_4m_second",  # pc-only
    0x0EE8E43F: "PA_SC_WINDOW_SCISSOR_BR",
    0x0EEBAE36: "uModel::MaterialGroup",
    0x0EEBC510: "cAnimColor::Key",  # pc-only
    0x0EECDE00: "TCA_TPC_DEBUG",
    0x0EF8D40B: "XUI_CONTROL_NAVIGATE",
    0x0EFCD1C9: "XAUDIO::XAUDIOSRCHDR",
    0x0EFFB6F1: "CP_IB2_BASE",
    0x0F023C1A: "GPUDIMENSION",
    0x0F059278: "MC0_CRC_READ",
    0x0F0A77F4: "_UCODE_DEFINITION_TABLE",
    0x0F0AADAA: "XAUDIOFXTABLEENTRY",
    0x0F0AB68C: "_U64",
    0x0F0C91AA: "cTrans::CMD_CALLBACK",
    0x0F0FF998: "_XMEDIA_VIDEO_DESCRIPTOR",
    0x0F10621D: "FSB_TR_DEBUG_HI",
    0x0F120658: "sRender::CAPS::VTF_TYPE",
    0x0F1453DA: "XVOICEMODE",
    0x0F164819: "PIX_NEXT_TIMING_CHUNK",
    0x0F179C88: "CONFIG_XSTRAP2",
    0x0F17A608: "RTS_BOUNDBOX_END",
    0x0F1EB126: "MtCollada::Scene",
    0x0F20D5B4: "D1OVL_PITCH",
    0x0F24EB1B: "CXrlTransaction",
    0x0F2B37BF: "MP4MediaInformationAtom",
    0x0F33AF45: "cTrans::CMD_SCISSOR",
    0x0F351C26: "rEffectList::NORM_ATTENUATE_FLAG",
    0x0F3C853D: "cOmCoopGateAction",  # pc-only
    0x0F3CC0D6: "_DVD_AP25_CHALLENGE_SET_HEADER",
    0x0F404C16: "tagWMVStartCodeSuffix",
    0x0F41F045: "cEm30ActSniffEnd",  # pc-only
    0x0F4AA3F6: "cEm42SAction",  # pc-only
    0x0F4C02D3: "_XHASH_STATE",
    0x0F4FF3FC: "rEffectSetData::ESD_MOVE_PATH_CHAIN",
    0x0F543E30: "cEmc0Action",  # pc-only
    0x0F5776E2: "_PASSPORT_LOGIN_EX_REQUEST",
    0x0F589BE1: "TCF_PERFCOUNTER7_SELECT",
    0x0F5F9C61: "CLittleEndianBuffer",
    0x0F607FF9: "cAINavMeshCostManager",  # pc-only
    0x0F625BA9: "cEm10ActDmgShieldBack",  # pc-only
    0x0F62DF3A: "cEm10ActAtkGunBomb",  # pc-only
    0x0F64872D: "MtFilePath",
    0x0F6A4D3F: "CP_RT6_MASK",
    0x0F6B1E7D: "cPositionFilterDoughnutAroundKeepPos",  # pc-only
    0x0F6B45E7: "SCL1_H_COUNTERS",
    0x0F6D199F: "uOma00c_UroAction::cActAct",  # pc-only
    0x0F6D7312: "uMirror::MyDTI",
    0x0F6DC816: "uShadow::MyDTI",
    0x0F6E51E8: "FSB_LX_PMCTRL_AND",
    0x0F6FE858: "uMovie",
    0x0F766C60: "AZ1_MRU_BANK18_DEPTH_MASK",
    0x0F7BEFA1: "XAUDIOFRAMEBUFINIT",
    0x0F8149A3: "sPrim::SCENECONTEXT",
    0x0F84C77E: "rterrmsgs",
    0x0F913CE3: "CP_IB2D_BUFSZ",
    0x0F92F2EB: "cEm84ActReadyBgn",  # pc-only
    0x0F956C1E: "GpuDecodeBuffers",
    0x0F991B90: "cEm6fActWait",  # pc-only
    0x0F9F3BA2: "_DXVA_COPPStatusInput",
    0x0FA0CADB: "AZ0_MRU_BANK19_DEPTH_MASK",
    0x0FA3A9ED: "EP_LATENCY",
    0x0FA70AED: "PIX_FRAME_DONE",
    0x0FA86B4F: "PA_SC_DEBUG_ITER_2",
    0x0FAA092F: "cPlAction_pl_act_gunemp_fire",  # pc-only
    0x0FAED0C7: "THREADTYPE_DEC",
    0x0FAF0978: "cEm0cActAppear",  # pc-only
    0x0FAF8508: "_IDE_IDENTIFY_DATA",
    0x0FAFBED4: "uPointCubeMapLight::MyDTI",
    0x0FB11547: "_VESA_MONITOR_RANGE_LIMITS",
    0x0FB46EFF: "VGT_GROUP_VECT_0_FMT_CNTL",
    0x0FB4F162: "_IMAGE_ALPHA_RUNTIME_FUNCTION_ENTRY",
    0x0FB9ECC4: "CCritSect",
    0x0FB9F232: "D3D::XBMCOMMAND_HANDLER",
    0x0FBBCE66: "cEm8cActWait",  # pc-only
    0x0FBC1BC9: "_IMAGE_ALPHA64_RUNTIME_FUNCTION_ENTRY",
    0x0FBE49A6: "_XPROFILE_SETTING_READ_RESULT",
    0x0FC33CC6: "cEm34ActTurn",  # pc-only
    0x0FC8402B: "cTrans::Element",
    0x0FC92DB3: "RB_EDRAM_TIMING",
    0x0FCBFEF3: "_currencyfmtA",
    0x0FD01A38: "uOmPlCopy::cActBase",  # pc-only
    0x0FD0A92D: "cPlAction_pl_act_wall_stick_turn_r",  # pc-only
    0x0FD32599: "cEm10ActDmgAtFaceDown",  # pc-only
    0x0FD48BB7: "_CQVal",
    0x0FDACBA9: "cShape::STATE",
    0x0FDCF5E3: "XONLINE_NAT_TYPE",
    0x0FDDB049: "tQWORD",
    0x0FE0DAEA: "cFSMOrderPawn::FuncParamDamage",  # pc-only
    0x0FE493B0: "CP_RT_DMA_COMMAND",
    0x0FE5F51F: "cEm66ActAtkSwimBiteHit",  # pc-only
    0x0FE8273D: "rEffectList::RELATION_SCALE_TYPE",
    0x0FE9BB1B: "uSingleLSM::MyDTI",
    0x0FEEA16F: "uOm08ac_Fence::cActFall",  # pc-only
    0x0FF18DC5: "rEffectList::KEYFRAME_TYPE",
    0x0FF24F03: "GPUPERFEVENT_SX",
    0x0FF585DE: "_XVOICEMAILUI_PARAMS",
    0x0FF73D22: "D1MODE_DATA_FORMAT",
    0x0FF76671: "cEm4501Action",  # pc-only
    0x0FFC2A70: "cNetEm42Tentacle",  # pc-only
    0x0FFC8EB3: "_CertEvents",
    0x0FFCB023: "_XMEDIA_AUDIO_DESCRIPTOR",
    0x0FFEA425: "SCL1_CONTROL1",
    0x1007780C: "DC_TEST_DEBUG_TRIGGER_CNTL",
    0x1007A8B9: "SSC",
    0x10083AB7: "uEffect2D::Sprite",
    0x1009CD40: "uCuboidCubeMapLight::MyDTI",
    0x100AF34D: "XUIMessageNavReturn",
    0x100DF9BF: "MP4FullAtom",
    0x1010BE31: "GPUCmdLoopFilter",
    0x1011925A: "RTS_BARYC_REF_VTX_X",
    0x1015F226: "D3D::_CounterRecord",
    0x10180B9D: "rEffectList::EFL_PARAM_CLOTH_CURVE",
    0x101BB434: "_FP__IEEE_FORMAT",
    0x1022B926: "uOm092e_LaserBlock::cActFall",  # pc-only
    0x1025A682: "rModelMontage::HEADER",
    0x102852AC: "cEm10ActSideStep_L",  # pc-only
    0x102961E3: "CP_ME_VS_EVENT_SRC",
    0x102A8431: "TCR_PERFCOUNTER1_SELECT",
    0x102BB51B: "MEM_BASE_LIMIT",
    0x102F6690: "SCL1_VFILT_IO",
    0x102FD4EE: "rScheduler::TRACK::TYPE",
    0x1032EC1F: "_HV_IMAGE_INFO",
    0x1035A4DF: "IO_BASE_LIMIT_HI",
    0x1036006C: "cEm30TentacleAction",  # pc-only
    0x10377DD2: "MtRandom",
    0x103F9EEE: "SB_EOIBAR",
    0x104275CF: "cEm43ActDie",  # pc-only
    0x10490FDF: "XGI_SESSIONSEARCH_MSG",
    0x104ABF3F: "FSB_TX_ERRCAP",
    0x104E9F3D: "_DUMP_SYSTEM_GLOBALS",
    0x1054EA21: "cMaterial::MyDTI",
    0x10597FFE: "sEffectVFR::__vftable",
    0x105B2509: "MP4SampleTableAtom",
    0x10652F2F: "std::ios_base",
    0x10684CD8: "D1CRTC_STATUS_VF_COUNT",
    0x10690E19: "ioinfo",
    0x106D57D4: "GPUEXECFETCHCACHETYPE",
    0x1070FB23: "cOmBoltActOpened",  # pc-only
    0x1072A82B: "uActorModel::Constraint::MyDTI",
    0x10766B69: "uOm0201_Piano::cEventActLeave",  # pc-only
    0x1077B3F5: "MtCollada::Array::MyDTI",
    0x1077C074: "NEWINDEX",
    0x107897BA: "SQ_FETCH_2",
    0x107AD18C: "strVideoStreamInfo_WMC",
    0x107FBE47: "_XSIGNATURE_LICENSE_ACKNOWLEDGMENT",
    0x10806E22: "sObjModel::LotSelector",  # pc-only
    0x1088CE6E: "cEm10ActAtkPlagaEat",  # pc-only
    0x108CD194: "_LDRX_SOURCE",
    0x108E3E6D: "cEm0bActAtkCatchHit",  # pc-only
    0x1092A270: "PCIE_CI_FLUSH_CNTL",
    0x109E66A7: "_XCONFIG_DVD_ENTRIES",
    0x109EB946: "NetworkSessionMcs::ConnectionParameter",
    0x10A89C52: "PatInterface::UserId",
    0x10ACD549: "_MEMORY_BASIC_INFORMATION",
    0x10B2C56B: "uOm1303_S109_Truck::cActMain",  # pc-only
    0x10B59B51: "FSB_TR_CTRL_OR",
    0x10B806E1: "cPlAction_pl_act_weapon_reload",  # pc-only
    0x10B8D60C: "_XMSG_SEND_RECIPIENT_RESULT",
    0x10B910DD: "cEm30TentacleActAttack",  # pc-only
    0x10BCBDE0: "AZ0_LOOPBACK_PATTERN2PHS3",
    0x10BCEB61: "aStageBase::MOVESCR_MATCHING",  # pc-only
    0x10C00511: "rModel::PARTS_INFO",
    0x10C13468: "cPlAction_pl_act_die_blow",  # pc-only
    0x10C460E6: "rMessage",  # pc-only
    0x10C68953: "NetworkStorageXbox",
    0x10CB4B6C: "cEm83ActCaught",  # pc-only
    0x10CC84F9: "CP_RT1_REFERENCE",
    0x10CE27B4: "uMovie::MyDTI",
    0x10CE855A: "D1GRPH_COLOR_MATRIX_CNTL",
    0x10DA0923: "uOmJeep::cActPlDeadFall",  # pc-only
    0x10DAE9DC: "_XFRIENDS_REQUEST_BY_NAME_PARAMS",
    0x10DD6F64: "_XNQOSHISTORYHEADER",
    0x10E4E13F: "uOma00e_UroWall::cActFall",  # pc-only
    0x10E73FD0: "RB_BC_CONTROL",
    0x10ED5BC4: "cEm60ActWaitMee",  # pc-only
    0x10ED5D41: "rPathXml",  # pc-only
    0x10F11674: "rSoundPackageXml::ProgramData",
    0x10F575EE: "cEm84ActDmgNormalU",  # pc-only
    0x10FC1828: "sPhysics::MassParticle::__vftable",
    0x10FE8B16: "_XINVITE_INFO",
    0x11005848: "cEm45ActQuake",  # pc-only
    0x1102F512: "cEm10ActDmgFlyoff",  # pc-only
    0x110E16F8: "IXuiTextureCache",
    0x110EF332: "XUI_BLEND_MODE",
    0x110F0D21: "uOm095e_Kick::cActWait",  # pc-only
    0x110FAC13: "rEffectSetData::ESD_MOVE_PATH_STRIP",
    0x110FCB35: "AZ0_MRU_BANK14_DEPTH_MASK",
    0x111777FC: "std::char_traits",
    0x1117B431: "cOma016PlEvent",  # pc-only
    0x111CBF74: "uOma004_Collapse::cActBase",  # pc-only
    0x112A2448: "uOm0026::cActInit",  # pc-only
    0x1133EE30: "_FXLEFFECT_DESC",
    0x1134BF72: "IUnknown::__vftable",
    0x11387F65: "cResource::__vftable",
    0x113B542B: "PatInterface::Storage",
    0x113D70B0: "_DRCOptions",
    0x113FA45D: "CHuffmanDecoder::__vftable",
    0x11458B43: "tagPlannedOutput_WMC",
    0x11476915: "uOmDive::cActPlBase",  # pc-only
    0x114A0715: "rEffectStrip::STRIP_TYPE",
    0x114BA1E7: "XAUDIO::CListEntry",
    0x114DF921: "XAUDIO::CObjectRefCount::__vftable",
    0x11506597: "SQ_ACTIVITY_METER_STATUS",
    0x11551BA4: "PA_SC_LINE_STIPPLE_STATE",
    0x11567265: "CP_DMA_SRC_ADDR",
    0x115720C1: "MtCollada::Skew",
    0x11573958: "uOmLaserMirror::cActPlTurn",  # pc-only
    0x115DB83C: "uEffectEmitter::PARENT_CONST_TYPE",
    0x115EA862: "PPXformStatus",
    0x116E4DFE: "_PASSPORT_CREATE_REQUEST",
    0x11710A80: "SCHEMA_EXTENDED_ATTRIBUTES",
    0x1177B83B: "uOm1317_Glass::cActWait",  # pc-only
    0x11786C76: "cFSMOrder::FuncParamOmEnd",  # pc-only
    0x117BC818: "uMultiRadialBlurFilter::RadialBlurParam",
    0x117E682D: "CCalMemoryQueue",
    0x117F120B: "uOm1316_BackupHeli2::cActAttack",  # pc-only
    0x11825036: "_XHTTP_REQUEST_RESPONSE",
    0x118505DA: "sResource::Property",
    0x1186DFC2: "_AP25_AUTHENTICATION_OUTPUT",
    0x11883AB4: "cEm34ActHang",  # pc-only
    0x11886E1F: "PatInterface::LayerInvite",
    0x11896574: "_D3DDEVTYPE",
    0x118C7C6A: "CP_ME_VS_EVENT_ADDR",
    0x118F9843: "TCR_PERFCOUNTER1_HI",
    0x11925EEB: "cEm10ActOverWindow",  # pc-only
    0x11928AFC: "_XPNGDECODE_PARAMS",
    0x1199EF9D: "uOma00b_LaserArea::cActWait",  # pc-only
    0x119D0EA1: "SQ_INPUT_ARB_PRIORITY",
    0x119E7B27: "cOm0200ActBack",  # pc-only
    0x119E7C0C: "NetworkRankingLive::Leaderboard",
    0x11A0C2D3: "cEm44ActDmgFall",  # pc-only
    0x11A0E999: "_SEMAPHORE_BASIC_INFORMATION",
    0x11A7A5F2: "_PASSPORT_GET_SECRET_QUESTIONS_REQUEST",
    0x11A7E0D4: "uDOFFilter",
    0x11AA9936: "cEm0bActDie",  # pc-only
    0x11AC8E76: "MtPlane",
    0x11ACF56C: "_SID_NAME_USE",
    0x11AE9B86: "_XRESOLVE_NAME_REQUEST",
    0x11B1E39B: "uOm095e_Kick::cActMotion",  # pc-only
    0x11B286D3: "DC_LUT_PWL_DATA",
    0x11B2BEA7: "_EVENT_BASIC_INFORMATION",
    0x11B96CE0: "_XCONFIG_SECURED_SETTINGS",
    0x11BF6DCC: "MtGeomCapsule::MyDTI",
    0x11C39651: "uShadowLight::MyDTI",
    0x11C3A296: "_XMATCH_SESSION",
    0x11C6E908: "sCollision::Param",
    0x11C763C6: "cTrans::CMD_PRIMINSTANCE",
    0x11C8F6F6: "CMediaStreamASFParser",
    0x11D14C1D: "cPlAction_pl_act_avoid_high",  # pc-only
    0x11D17B7E: "cPlAction_pl_act_turn_r",  # pc-only
    0x11D33203: "uOmSwitch3::cActMid2Pull",  # pc-only
    0x11D3E153: "_XARB_REPORT_SUSPICIOUS_INFO",
    0x11D6096A: "XCUSTOMACTION_FLAGS",
    0x11D96D8E: "AZ1_MRU_BANK15_DEPTH_MASK",
    0x11E31C84: "cLayoutSprite",  # pc-only
    0x11E9C410: "COHER_SIZE_RT",
    0x11ED2A7F: "princeton_digital::eq1_t",
    0x11EDABFE: "uRadialBlurFilter",
    0x11F1A392: "_MM_KERNEL_STACK_TYPE",
    0x11F1D42D: "RTS_EDGE_0_DIST_LSBS",
    0x11F5DE30: "SQ_CF_RD_BASE",
    0x11F7E391: "cAIFSMManager::OwnerInfo",  # pc-only
    0x11FAC75D: "cEm84ActReadyTurn",  # pc-only
    0x11FB5082: "SCL1_HFILT_COEF",
    0x11FBC512: "rEffectAnim::EAN_HEADER",
    0x11FD728B: "MH_PERFMON_PERFCOUNTER0_HI",
    0x11FD89D7: "D3D::D3DQUERYSTATE",
    0x11FEE6FD: "XUIPropertyData",
    0x1200A447: "NetworkMultipleUdp",
    0x12010601: "PatInterface::CircleName",
    0x1201A0BB: "MtColorF",
    0x12022D10: "_numberfmtA",
    0x1203E8F1: "std::bad_alloc",
    0x1209452F: "PatInterface::UserInfo",
    0x1209F04A: "AZ0_MRU_BANK10_DEPTH_MASK",
    0x120B35F2: "cEm71ActReact",  # pc-only
    0x1210520F: "_CERTIFICATE_LOG_ENTRY",
    0x12105B9F: "cEm0bActGetup",  # pc-only
    0x1211EBA7: "cEm83PlEvent_Pinion",  # pc-only
    0x1214A970: "cEm40ActSSUDamage",  # pc-only
    0x1215F684: "_D3DPWLGAMMA",
    0x1219C4D4: "D3D::RingBufferState",
    0x121B5A94: "EXTCONTENTDESC",
    0x1221B038: "ROOT_CONTROL",
    0x1221E03B: "SQ_PERFCOUNTER2_SELECT",
    0x1223798A: "cEm10ActNeckHangDmg",  # pc-only
    0x122BC5E8: "CCalChannel",
    0x12341A62: "D1MODE_DESKTOP_HEIGHT",
    0x123BC309: "MH_INT_SIGNAL",
    0x123D8211: "rEffectSetData::ESD_MOVE_PATH_KEYFRAME",
    0x123F3F94: "MtCollisionEpa::MtEpaLocalList::TListElem",
    0x123FF8DD: "cEm82DmgLastPinionDie_PL",  # pc-only
    0x1245152E: "XGI_READSTRING_MSG",
    0x12469F7F: "CCalEncoder",
    0x124C18B2: "_XCONFIG_USER_ENTRIES",
    0x124D0300: "uFlatWater::WATER_VERTEX",
    0x12514962: "cOmBoatAirActionPl",  # pc-only
    0x125B98DD: "_D3DPOINT",
    0x125E0E6F: "SurfaceEndian",
    0x125FE632: "cEm63ActWait",  # pc-only
    0x12615BBF: "_XBOX_LIBRARY_VERSION",
    0x1261AC92: "cEm6dActGoToFly",  # pc-only
    0x1265A094: "uColorCorrectFilter",
    0x126972E4: "EP_DEVICE_ID",
    0x1269FE11: "princeton_digital::eq3_t",
    0x126A2F60: "uOm095a_Jump::cActWait",  # pc-only
    0x126AD8E0: "rMovie",
    0x126D6CD5: "ID02_DMIF_DCP_DATA_RETURN2",
    0x126E63B3: "rEffectList::EFL_INDEX",
    0x126F2E96: "TCO_QUAD2_DEBUG1",
    0x126F7D87: "CP_RT1_MASK",
    0x12709070: "cAIBlackBoardMessage",  # pc-only
    0x12715778: "uMovie::Player::Status",
    0x12727163: "IRQ_BRIDGE_CNTL",
    0x1273A621: "TCD_DXTMUX_SCTARB_DEBUG",
    0x1273CB01: "_P_LIST_CHANGE_ITEM",
    0x1276393B: "rFacialAnimation::MyDTI",
    0x127AE913: "_D3DTEXTURESTAGESTATETYPE",
    0x127E4091: "NetworkLayer::PositionReceive",
    0x12886BE1: "BIOS_4_SCRATCH",
    0x128CE742: "_SGADDR",
    0x128E55A7: "rModelMontage::__vftable",
    0x128F3EF9: "CP_INT_CNTL",
    0x12904066: "AHShapeBox",  # pc-only
    0x1292C392: "cEm60Action",  # pc-only
    0x129307B8: "cJointEx",  # pc-only
    0x1293F818: "XUIMessageSourceText",
    0x1294BC35: "_XUSER_PLAYER_ENUM",
    0x1294E19D: "VGT_GROUP_VECT_1_CNTL",
    0x129A7471: "cWpAction_wp0d_act_load_first",  # pc-only
    0x129A8F98: "cEm84ActHang_ReadyEnd",  # pc-only
    0x12A59FCB: "CXuiVideo",
    0x12A613C0: "MtMemoryCachedStream::MyDTI",
    0x12A6EAD9: "sPad::PAD_VIB_LIST",
    0x12B0F04A: "uEffectVFR::Polygon",
    0x12B5E8AE: "ROM_PADS_REG",
    0x12B927B2: "_D3DXPLAYBACK_TYPE",
    0x12BAA05B: "PCIE_VC0_RESOURCE_CNTL",
    0x12BEA500: "XUIMessageTopItem",
    0x12C6068E: "AZ1_LOOPBACK_PATTERN2PHS0",
    0x12C7DBDA: "PA_SC_DEBUG_CW_3",
    0x12C8FD5A: "SXIFCCG_DEBUG_REG2",
    0x12C90632: "rSoundEngine::EngineCurveData",  # pc-only
    0x12C91BB6: "FexMvRangeType",
    0x12C92C74: "uOm1303_S109_Truck::cActExplosion",  # pc-only
    0x12D16F3A: "CP_RT_BIN_MASK_LO",
    0x12D2103E: "rEffectList::EFL_MOVE_MUL",
    0x12D31340: "XMAWAVEFORMAT",
    0x12D4749F: "SQ_INSTRUCTION_CF_JMP_CALL_0",
    0x12D966DF: "uEffectEdit::STATUS",
    0x12DCFF0A: "cEm32ActFall",  # pc-only
    0x12DF56F1: "AZ1_MRU_BANK11_DEPTH_MASK",
    0x12E4C1EA: "RBBM_INT_ACK",
    0x12E51EE5: "MtCollada::Param::FLOW",
    0x12ED9B24: "sSoundN::MyDTI",
    0x12EDFA22: "uModel::RenderInfo::MyDTI",
    0x12EEADB6: "uGridEnvLight",
    0x12F254C3: "TCF_PERFCOUNT_SELECT",
    0x12F7F202: "_XPROFILE_RACE_TRANSMISSION_OPTIONS",
    0x12F919D1: "SLOT_CAP",
    0x12FC6863: "RB_BLEND_RED",
    0x12FCE9BA: "PA_SC_VIZ_QUERY_STATUS_1",
    0x12FF7785: "IXAudioSourceVoice",
    0x12FFB9F1: "sApp::Item::ATTR",
    0x1308112C: "XNetCapFrame",
    0x13092AA0: "cOmCoopDoorAction_om_act_down",  # pc-only
    0x130A9EAC: "PatInterface::CircleUserNtc",
    0x130F516C: "cEm0cActErase",  # pc-only
    0x1310D942: "_DXVA_DestinationFlags",
    0x13146AD2: "SQ_FETCH_RT_5",
    0x1318A835: "uEffectVFR::Model",
    0x1322E595: "uEffectEdit::PTCL_MOVE_RNO_TBL",
    0x1326185C: "_D3DPATCHEDGESTYLE",
    0x13272207: "cTrans::SCENE",
    0x13291888: "_HEAP_UCR_SEGMENT",
    0x132D17E4: "uOmCoopSwitch_S301::cActFinish",  # pc-only
    0x133175CC: "sGpuParticle::PIPELINE_PRIM",
    0x1331FAF6: "BRTSTATUS",
    0x13339AC9: "FSB_LX_PMC0",
    0x133664C7: "_D3DXMACRO",
    0x1338178F: "_DXVA_DeinterlaceCaps",
    0x133EB612: "NetworkRankingLive::BoardMap",
    0x13408FE0: "uOmElevator::cActPlBase",  # pc-only
    0x1340C3EC: "NetworkLayer::Delivery",
    0x13417F97: "RBBM_PERFCOUNT2_SEL",
    0x13426C94: "XMEDIAFORMAT",
    0x1344ACCF: "TCM_PERFCOUNTER1_LOW",
    0x134B891A: "XG_MCT::CXEncoder::__vftable",
    0x134EDF13: "cEm10ActWallWaitL",  # pc-only
    0x134F2BE8: "_FXLDATA_TYPE",
    0x13532571: "ID3DXLine",
    0x1354C662: "D3DXVECTOR3_16F",
    0x1355AA07: "cOmLockActDamage",  # pc-only
    0x135A5AA3: "MtCollada::Image",
    0x135C6272: "sCollision::cColTree::TREE_MODE",
    0x135E2974: "cFSMOrder::FuncParamSimpleEv",  # pc-only
    0x13671892: "cOmCoopGateAction_om_act_wait",  # pc-only
    0x136751EA: "_HARDWARE_SCALER_PARAMETERS",
    0x136DF061: "rCloth::Header",
    0x136FE91E: "VC_PERFCOUNTER3_LOW",
    0x1372E614: "cEm84PlEvent_DownStripEnd",  # pc-only
    0x1372F4F5: "_XBOX_KRNL_VERSION",
    0x137BA8FE: "_XACCOUNT_GET_ANID_RESPONSE",
    0x137CB3C6: "uCapsuleCubeMapLight",
    0x137F8B04: "cEm84ActWalkEnd",  # pc-only
    0x137FF190: "XAMDATEFORMAT",
    0x1382C2E9: "rEffectList::END_TYPE",
    0x1382E998: "rEffectList::ADHESION_TYPE",
    0x138B0B54: "_DISK_GEOMETRY",
    0x138BBCC2: "CSystemApp::__vftable",
    0x138FAC90: "REG_MACRO_ADDR_0",
    0x1390FCD3: "uSynchroSpotLight::MyDTI",
    0x1398B9F2: "rSoundAttributeSe::cSoundAttributeSeData",  # pc-only
    0x139F0937: "HSIO_OVERRIDE_OE",
    0x13A1808C: "GPUCOPYCOMMAND",
    0x13A387FC: "cPlAction_pl_act_plaga_stick_in",  # pc-only
    0x13A591AA: "XAUDIO::SRC::Linear",
    0x13A72E8E: "cAIDynamicPathFinding::TraceManagement::Trace",  # pc-only
    0x13AB6C9A: "GPUCOMMANDOP",
    0x13AB9426: "princeton_digital::eq2_t",
    0x13AC9514: "XMA2WAVEFORMAT",
    0x13B51856: "_IMAGE_NT_HEADERS64",
    0x13BA4733: "XUI_LINECOUNT",
    0x13BCA924: "cMaterial::FUNC_SKIN",
    0x13C6F030: "CP_CSQ_AVAIL",
    0x13C97C8C: "rEffectSetData::ESD_SET_MODEL",
    0x13CF3CC5: "CP_2D_BRUSH_BASE",
    0x13D626C8: "t_AltTablesDecoder",
    0x13D6ADB2: "D3D::D3DPACKET_STATE",
    0x13D84CE8: "rEffectList::REACTION_TYPE",
    0x13DBD4E3: "_PM4CMDNOP",
    0x13E1D0C9: "IOC_PERFCOUNTER3_HI",
    0x13E1FDFD: "cEm41AActMissileCatch",  # pc-only
    0x13E5866E: "cFSMOrder::FuncParamS32",  # pc-only
    0x13E78E27: "_DIRECTORY_ENUM_CONTEXT",
    0x13F1C05B: "CXMsgSendBase::__vftable",
    0x13FB414F: "D1GRPH_PRIMARY_SURFACE_ADDRESS",
    0x14016F9A: "sCubeMapInterp::BakeInfo",  # pc-only
    0x1401A0BC: "VGT_ENHANCE",
    0x14035625: "cEm22ActAtkCutsDown",  # pc-only
    0x14044491: "uOmCoopSwitch_S301::cActPlBase",  # pc-only
    0x140586B4: "AZ0_MRU_BANK18_DEPTH_MASK",
    0x140786A1: "MtAllocator::TYPE",
    0x140943A4: "_BANNER_GET_HOTLIST_REQUEST",
    0x1416D07B: "MtCollada::Sampler::MyDTI",
    0x14190986: "cTrans::Technique",
    0x14191A60: "uOmCrouch::cActBase",  # pc-only
    0x1419A8F4: "_XPROFILE_TITLE",
    0x141D62B6: "PCIE_TX_CREDITS_CONSUMED_CPLD",
    0x141EE6F0: "_FIND_USERS_REQUEST",
    0x1422F731: "VGT_DMA_BASE",
    0x142437DC: "_EX_THREAD_REGISTRATION",
    0x142C1C56: "cFSMOrder::FuncParamChapter",  # pc-only
    0x1431ECD8: "cEm84ActStrippedEnd",  # pc-only
    0x14324F60: "rSoundSourceMusicInterMediate",
    0x14341319: "uCoord::ORDER",
    0x14347FB5: "PerChannelInfoDEC",
    0x1434F296: "cEm32ActMountMiss",  # pc-only
    0x1436D3B6: "rEffectAnimation::EFA_HEADER",
    0x1438876D: "MP4DataEntryURLAtom",
    0x143B01C2: "_FPIEEE_FORMAT",
    0x1441EDAF: "RB_HSIO_PHASE_INIT",
    0x144FCF62: "EFC_PARAM_F32",
    0x14538CC1: "TCF_PERFCOUNTER3_LOW",
    0x1454EA9D: "uOm0941::cAction_break",  # pc-only
    0x1456F934: "XAUDIO::CMemoryTracker",
    0x145E5ED0: "FSB_LX_PMC4",
    0x145F26EE: "_D3DSCREENEXTENTQUERYMODE",
    0x1462A3E3: "cEm32ActWait",  # pc-only
    0x146ABF3E: "_CDROM_TOC",
    0x146FFC5B: "MP4TrackFragmentHeaderAtom",
    0x14735482: "EFC_KEYFRAME_U16",
    0x1473F4DF: "_XNPSOCKETSECURITY",
    0x1477DABE: "_XDASHLAUNCHDATA",
    0x14799A5C: "XMEDIA_CALLBACK_TYPE",
    0x1479AECB: "SQ_FETCH_RT_1",
    0x147B1E05: "NetworkPhysicalAddress",
    0x147B8A70: "_FIND_MEDIA_INSTANCE_URLS_REQUEST",
    0x14845FDE: "D1MODE_VLINE_START_END",
    0x14884C3F: "MP4ESDAtom",
    0x148AAB60: "cPlAction",  # pc-only
    0x148AEE90: "VGT_MIN_VTX_INDX",
    0x148F4BB0: "PGL_CTL0",
    0x1496D88C: "uModelPlaneClip",
    0x14990D55: "cOmCoopCardDoorActWait",  # pc-only
    0x149DA435: "XDVO_CLOCK_INV",
    0x14A4CC49: "uImagePlaneFilter",
    0x14A590A9: "cTrans::ENVELOPE",
    0x14A9656D: "XAUDIOFXTABLE",
    0x14AA843B: "uEffectEdit::MyDTI",
    0x14B0E44B: "D3D::_D3DPATCH",
    0x14B20753: "_XCONFIG_POWER_MODE",
    0x14B2A05C: "_HEAP_LOCK",
    0x14B4924C: "COHER_STATUS_PM4",
    0x14BED49A: "_DUMP_MEDIA_SERVICES",
    0x14BF2141: "ID3DXSPMesh::__vftable",
    0x14C14C3E: "cEm10ActAtkGunEmpRideOff",  # pc-only
    0x14C3359A: "cTrans::CMD_ZPASS",
    0x14C6F0F2: "rModelMontage::MONTAGE",
    0x14C8B3F1: "_P_TEAM_MANAGE_MEMBER_MSG",
    0x14C9D4C7: "_Q_MESSAGE_DETAILS_MSG",
    0x14CA3BDD: "NetworkMultipleUdpLive",
    0x14CF3BFF: "sPrim::FUNC_PRIM_BASEMAP",
    0x14D3200F: "AZ1_MRU_BANK19_DEPTH_MASK",
    0x14D71C76: "AZ0_SECONDARY_STATE_DWORD3",
    0x14D8A0D5: "EFC_KF_REF_TYPE",
    0x14D8E98F: "uCuboidCubeMapLight",
    0x14D8FDBF: "PIX_STREAM_OPTIONS",
    0x14D997F7: "cNetEm0b",  # pc-only
    0x14DA9312: "CP_NV_FLAGS_1",
    0x14DE7761: "XCOMPRESS::_LZXDECOMPRESSION_CONTEXT_HEADER",
    0x14E083B9: "AIFFMARKER",
    0x14E26889: "REG_MACRO_ADDR_4",
    0x14E42A90: "PIX_CHUNK",
    0x14EBA32F: "uOmCrank::cActBase",  # pc-only
    0x14EED600: "BIU_CNTL",
    0x14F00382: "PCIE_TX_CREDITS_LIMIT",
    0x14FB0F29: "CP_RT2_MASK",
    0x1502177E: "cFSMOrder::FuncParamMap",  # pc-only
    0x1503F606: "_MEMORY_REGION_TYPE",
    0x1505C663: "VGT_PERFCOUNTER3_SELECT",
    0x15071FAF: "rEffectSetData::ANM_OPTION_FLAG",
    0x150FA566: "_PMD",
    0x1510C0EE: "FSB_TX_DEBUG_AUX_OR",
    0x1517D5DD: "cEm84ActPinioned",  # pc-only
    0x1519B1FC: "uEffectEdit::MoveMulKeyframe",
    0x1520C88C: "NetworkXboxVoice::__vftable",
    0x1520CF1D: "AIFFSOUNDHDR",
    0x1525228A: "cEm8cAction",  # pc-only
    0x1528D1C7: "_OSVERSIONINFOEXW",
    0x152F1E8A: "_XNPXMITRECVSTATS",
    0x15302EF4: "rLayout",  # pc-only
    0x153043EF: "SCLK_PWRMGT_CNTL2_REG",
    0x153125BB: "cOmLadderActionV_wait",  # pc-only
    0x15313967: "FSB_LX_LERST_XSTP_AND",
    0x153B854E: "sCamera::Viewport::FOG_TYPE",
    0x153D92E5: "FSB_TX_DEBUG_LO",
    0x1546C829: "CCalMediaInfo::__vftable",
    0x15470D90: "_CONTENT_ENUMERATE_REQUEST",
    0x15471788: "cEm4502ActDisappear",  # pc-only
    0x15472CBC: "aS109::cActEvPlBikeAppear",  # pc-only
    0x15486135: "cEm10ActWallAimL",  # pc-only
    0x154974AA: "uEffectVFR::GEN_RNO_TBL",
    0x1555521D: "RB_PERFCOUNTER3_LOW",
    0x1558AA53: "rEffectSetData::ESD_MOVE_MUL_COLL",
    0x1558B981: "XONLINE_TIER_TYPE",
    0x155B82AB: "tDecodeDispRotateDegree",
    0x155BB03F: "_XPROFILE_CLEAR_TITLE_REQUEST",
    0x1561ABE0: "NB_DEVICE_ID",
    0x1563B14E: "VGT_HOS_MIN_TESS_LEVEL",
    0x1565187B: "XONLINE_TAX_TYPE",
    0x1568823D: "cEm20ActWarn",  # pc-only
    0x1568874F: "sPad::DECIDE_BUTTON",
    0x15692485: "uFilter",
    0x156D6C4E: "FSB_LX_PMC2_OR",
    0x157389D3: "rEffectSetDataList::ESL_SET_COMMON",
    0x15756743: "uOmSwitch3::cActMessage",  # pc-only
    0x1575C31B: "AZ0_RESET_SAMPLE_COUNTERS",
    0x1578ACED: "CP_ME_RAM_WADDR",
    0x15807B37: "MtCollada::Pass",
    0x1580C9D7: "_PASSPORT_ENCRYPTED_PROXY_PARAMETERS",
    0x1584A937: "rEffectList::PARTICLE_TYPE",
    0x1587DE19: "D1GRPH_LUT_10BIT_BYPASS_CNTL",
    0x158A2BA6: "cEm10ActBackHold_PL",  # pc-only
    0x158EFA9A: "XECRYPT_RSAPRV_4096",
    0x159104A9: "FSB_LR_CTRL_AND",
    0x159285C5: "cObjAdjTree",  # pc-only
    0x159ED7F4: "HANDLERENTRY",
    0x15A19CFD: "XML_SUBELEMENT_DATA",
    0x15A3F2D8: "DCCG_SCLK_R_DISP_CNTL",
    0x15A7B638: "ID3DXFileDataVtbl",
    0x15AAAA3F: "PCIE_UNCORR_ERR_STATUS",
    0x15ACC990: "D3DArrayTexture",
    0x15B995F3: "XAUDIOVOICEOUTPUTVOLUME",
    0x15BA76FB: "BIU_PERFCOUNTER0_HI",
    0x15BD7C80: "cPlAction_pl_act_die_fire",  # pc-only
    0x15BEC55C: "cEm30ActBark",  # pc-only
    0x15C95626: "linger",
    0x15CCBC06: "XUI_NAMEDFRAME_COMMAND",
    0x15CD0BEA: "cEm34ActBlown",  # pc-only
    0x15CE311C: "VC_PERFCOUNT_SELECT",
    0x15D074CC: "SCL1_READBBUF_IO",
    0x15D091E0: "D1CRTC_BLANK_DATA_COLOR",
    0x15D20250: "_DVD_XGD2_DISC_AUTH_RESULT_CHALLENGE_COUNT",
    0x15D28ADA: "AIFFMARKERHDR",
    0x15D39165: "_XNPGREYLISTADDRESSENTRY",
    0x15D8846F: "sPad::Pad",
    0x15D8891F: "cFSMOrderEm30::FuncParamSetAction_Em30",  # pc-only
    0x15DA3AD4: "_D3DXFRAGMENT_DESC",
    0x15DBECDB: "PatInterface::MediaVersion",
    0x15DFF025: "cEm41ActDiscloseDamage",  # pc-only
    0x15E3C2A8: "GpuCopy",
    0x15EA92EE: "rSoundSourceSE::MyDTI",
    0x15ED233C: "sSoundN::REVERB_PARAMETER",
    0x15EE6D67: "MtGeomTriangle::TRI_VORONOI_ID",
    0x15F24D89: "GPUANISOFILTER",
    0x15F27951: "AZ1_SECONDARY_STATE_DWORD3",
    0x15F7D289: "std::invalid_argument",
    0x15FC736E: "cBioTree",  # pc-only
    0x16021C59: "cPositionFilterDoughnutAroundPos",  # pc-only
    0x16022D1A: "_XCONFIG_SYSTEM_SETTINGS",
    0x16060B9E: "MtCollada::Perspective::MyDTI",
    0x160B847D: "MtCollada::Element::MyDTI",
    0x160E21CC: "cFSMOrderPlayer::FuncParamAreaHitPl",  # pc-only
    0x1612CED3: "cEm84ActDmgKnockDown",  # pc-only
    0x16139AD0: "EdramMode",
    0x161678B9: "ID13_BLEND_DATA_R",
    0x1619719C: "uScheduler::MyDTI",
    0x161A1299: "uEffectVFR::MoveNone",
    0x161A9537: "uSynchroPointLight::MyDTI",
    0x161AD833: "DC_TEST_DEBUG_EDGE_TRIGGER_PATTERN",
    0x161C7926: "_XSESSION_SEARCHRESULT",
    0x16266500: "cEm42ActCoreHide",  # pc-only
    0x162A27A2: "FSB_LR_DEBUG_LO",
    0x162C4EA7: "MtMemoryCachedStream",
    0x162FB99C: "RTS_INV_W_DY",
    0x1630F3D1: "sSoundN::MultiBandEQ",
    0x1632C33F: "GPUREGISTER",
    0x1636C925: "D3D::CVertexDeclaration",
    0x1638869C: "MtRangeU16",
    0x1639845A: "_SCSI_PASS_THROUGH_DIRECT",
    0x163A7384: "_D3DPERFCOUNTER_EVENTS",
    0x163EE69E: "uEffectVFR::LINE_ZIGZAG_WORK",
    0x163FDA35: "HdrDecodeFltParStatus",
    0x1642F70E: "tagSTREAM_SEEK",
    0x16445473: "rSoundSource::RIFF_CHUNK",
    0x1645B991: "AIFFLOOP",
    0x1648DEB0: "ID3DXFileEnumObject",
    0x164C19AE: "XAUDIO::CFrameBuffer::__vftable",
    0x16585F1D: "VC_DEBUG_CNTL",
    0x1658E2C9: "princeton_digital::onetap_t",
    0x165ABDD6: "uOma00e_UroWall::cActWait",  # pc-only
    0x166197B2: "RB_HSIO_DLL_ADJ8",
    0x16680C98: "_D3DXEFFECTDEFAULT",
    0x166A86D9: "aS116::cActCloseBolt",  # pc-only
    0x166AC83F: "D3D::BracketType",
    0x166B321B: "FSB_LX_LERSTM_OR",
    0x166C980C: "MtPreProcessor::Include::__vftable",
    0x167131A6: "cFSMOrder::FuncParamCheckObjModel",  # pc-only
    0x16734B70: "D3DXCOLOR",
    0x1675C685: "cEm44ActWalkEnd",  # pc-only
    0x16784FF7: "cEm43ActChildAttack",  # pc-only
    0x16793010: "rHit::Node",  # pc-only
    0x167A6809: "MtClipboardStream",
    0x167A81FC: "rEffect2D::E2D_INDEX",
    0x167C7D80: "NetworkUniqueId",
    0x167DBBFF: "rSoundStreamRequest",
    0x1684428C: "CCalBase",
    0x1686B1EE: "FSB_TX_CTRL_AND",
    0x168937DB: "cWpAction_wp0d_act_fire_erase",  # pc-only
    0x168AB64E: "TCF_DEBUG",
    0x1690F381: "XG_MCT::CSimpleDecodeModel",
    0x1692439E: "FSB_LR_ERRCAP",
    0x1692E62C: "CLIPPER_DEBUG_REG08",
    0x16959A47: "PA_SU_SC_MODE_CNTL",
    0x169836B2: "MtCollisionGjk::MyDTI",
    0x169CE5CF: "uOm092e_LaserBlock::cActWait",  # pc-only
    0x169FD867: "_PM4CMDDRAWINDXIBINDX",
    0x16A13AF5: "PA_SC_DEBUG_ITER_1",
    0x16A97F7E: "_audecInputParams",
    0x16AA76DD: "cEm44ActAtckDash",  # pc-only
    0x16B173AC: "CIcsInfo",
    0x16B7CD52: "uTextureBlend::BLEND_MODE",
    0x16B88EBC: "CCalCustomStream::__vftable",
    0x16C9D9FD: "rSoundCurveSetXml::BasicCurves",
    0x16D3B5A7: "SB_ADAPTER_ID",
    0x16D496F6: "_EXCEPTION_RECORD",
    0x16D4D201: "CP_STAT",
    0x16D8CD68: "cEm20Action",  # pc-only
    0x16DB6A82: "std::bad_typeid",
    0x16E1DA2C: "_IMAGE_BASE_RELOCATION",
    0x16E1DCED: "D1SCL_VERT_FILTER_INIT",
    0x16E34165: "_DM_HDD_READWRITE_REQUEST_DATA",
    0x16E94E6A: "CP_OP",
    0x16E9C70A: "CXStorageDownloadToDirectory",
    0x16EC0529: "_DXVA_BlendCombination",
    0x16EC8663: "CXuiSound",
    0x16EFD6E5: "_P_PRESENCE_INITIALIZE_MSG",
    0x16F0B334: "_P_PEER_SUBSCRIBE_MSG",
    0x16F7F59F: "SCL1_CONTROL2",
    0x16F8ED4B: "sParameter::ENEMY_INFO_STRUCT",  # pc-only
    0x16FFB8BC: "CJointStereoData",
    0x170362B9: "rEffect2D::RT_OPTION_FLAG",
    0x1707D591: "FSB_LX_VCARB_OR",
    0x170CA765: "FSB_LX_LERST_AND",
    0x170DD6D4: "uOm0912_s119Tram::cActWait",  # pc-only
    0x170F07AA: "cEm42ActCoreDamage",  # pc-only
    0x17107290: "CXuiElement",
    0x1711DADD: "cFSMOrder::FuncParamMessageNPC",  # pc-only
    0x1715E959: "D3D::CBlocker",
    0x1718BEE9: "TRADEOFFHINT",
    0x1719E483: "_XCOMPRESS_BLOCK_HEADER_LZXNATIVE",
    0x171A75D8: "_QUOTA_LIMITS",
    0x171BC916: "_KDRIVER_NOTIFICATION_REGISTRATION",
    0x17224947: "DBG_CNTL1_REG",
    0x1722CBD0: "MALLOCSTATE",
    0x172995F4: "XUIMessageDiscardResources",
    0x172A2EDE: "cEm10ActAtkChainLong",  # pc-only
    0x172BA3AD: "cPlAction_pl_act_wall_stick_t_ready_knife_direct",  # pc-only
    0x1734D463: "_FILE_DISPOSITION_INFORMATION",
    0x1735D49B: "_DVD_XGD2_DISC_AUTH_RESULT_CODE",
    0x1738A31A: "PIX_INDEX_LOCATION",
    0x173C6514: "_XCONFIG_IPTV_ENTRIES",
    0x173D1929: "uOm0944::cActWaitToDown",  # pc-only
    0x173F5A33: "XDVO_FORCE_OUTPUT_CNTL",
    0x173F8E25: "EXTERN_TRIG_CNTL",
    0x17429CBB: "rEffectList::EFL_PARTICLE_SPOT_LIGHT",
    0x1742A313: "stMemTraceContext",
    0x1747D986: "cPlActionSub",  # pc-only
    0x17482381: "sCollision::Collider::MyDTI",
    0x174D8654: "_CDROM_PLAY_AUDIO_MSF",
    0x174DA5BE: "SQ_PERFCNT_SELECT",
    0x174E805A: "D1SCL_HORZ_FILTER_INIT_RGB_LUMA",
    0x174F15CB: "XONLINE_OFFERING_FREQUENCY",
    0x17590375: "CCalBase::PLAYER_STATE",
    0x1759C36B: "XONLINE_CREDIT_CARD_TYPE",
    0x175F8B3C: "cTrans::Element::MyDTI",
    0x17621D3F: "cEm30PlEvent_NeckBiteHit",  # pc-only
    0x1762E1D3: "_D3DADAPTER_IDENTIFIER9",
    0x1765BC7B: "CONFIG_XSTRAP",
    0x17665F33: "cTrans::CMD::TYPE",
    0x17668353: "cOmAction",  # pc-only
    0x1766DC1F: "cEmc0ActAttack",  # pc-only
    0x176C1FDC: "cOmJeepAction_om_act_dead_fall",  # pc-only
    0x176FB7AA: "INTERRUPT_PIN",
    0x17735EA3: "D1CRTC_STATUS",
    0x17788057: "EffectArrayElement",  # pc-only
    0x177B552B: "GpuResidualInfo",
    0x177B5814: "CCalCustomStream",
    0x177C5A38: "IXAudioFrameBuffer",
    0x177C5CF0: "sShader::TechniqueDesc::MyDTI",
    0x177EACED: "rEffect2D::E2D_PARTICLE_COMMON",
    0x17845404: "MtCollision::LocalBlockAllocator",
    0x17849E98: "rEffect2D::KEYFRAME_REF_TYPE",
    0x1786C8EB: "CXStorageUploadFromDirectory",
    0x179B4621: "cEm10ActAtkGunEmpRide",  # pc-only
    0x17A2E63B: "cTrans::Technique::SHADER",
    0x17A421C3: "PatInterface::CircleInvite",
    0x17A4817D: "cEm40ActTakeErase",  # pc-only
    0x17A69ACE: "rMovieOnMemoryInterMediate",
    0x17AA116B: "_IMAGE_AUX_SYMBOL",
    0x17AB5700: "FSB_LX_LERSTM_AND",
    0x17B13EE6: "XAUDIO::XMA_PLAYBACK_STATUS",
    0x17B260B7: "_HEAP_TAG_ENTRY",
    0x17B44B87: "_CACHEHASHTABLEENTRYWITHREFCOUNT",
    0x17B64299: "_DXVA_Slice_H264_Long",
    0x17B67883: "uSpotMapLight",  # pc-only
    0x17B9F83B: "XHVRESAMPLER",
    0x17BA166F: "cEm10ActDmgGG2",  # pc-only
    0x17BB4C4C: "RB_BLENDCONTROL3",
    0x17BC9B0B: "cAIFSMFunc",  # pc-only
    0x17BC9C4E: "_DXVA_Slice_H264_Short",
    0x17BD90AE: "_IMAGE_DOS_HEADER",
    0x17C36769: "D3D::HangGroup",
    0x17C3F11E: "_UTILITYDRIVEREQUEST",
    0x17C54661: "rEffectSetData::ESD_SET_COMMON",
    0x17C9E69B: "cEm20ActAtkCombo4",  # pc-only
    0x17CC8F07: "cTrans::VertexDecl::MyDTI",
    0x17CFEF95: "cEm52ActKamikaze",  # pc-only
    0x17D46024: "DEVICE_ID",
    0x17D597CD: "cPlAction_pl_act_item_dump_first",  # pc-only
    0x17D8C9BE: "MtFile::MODE",
    0x17DB19F3: "TCM_PERFCOUNTER1_SELECT",
    0x17DC240B: "FSB_TX_PMC4_AND",
    0x17DCBD4A: "XHVENGINECREATEPARAMS",
    0x17E79FD7: "CXHttpDownloadToMemory",
    0x17EC5FCD: "CP_RT4_COMMAND",
    0x17ED806C: "GPUSIGN",
    0x17F411E7: "rModel::JOINT_INFO",
    0x17FA2059: "IUnknownVtbl",
    0x17FC3BA1: "uOmEvade::cActBase",  # pc-only
    0x18049152: "CP_IB2_BUFSZ",
    0x180D7D56: "rSoundCurveSetXml::BasicCurves::MyDTI",
    0x18120E60: "cEm8cAtkArmLoop",  # pc-only
    0x1814053A: "_DUMP_FRAME_BUFFER_INFO",
    0x1814D6F6: "sCollision::cColTree",
    0x18157170: "MC1_PAD_IF_CNTL_2",
    0x181986EF: "rSoundStreamRequest::SOUND_STREAM_REQUEST_EFFECT_CATEGORY",
    0x1820355A: "CP_RT_ME_RDADDR",
    0x18248E4E: "cEm10ActDownRoll_R",  # pc-only
    0x182966B9: "_FP_IEEE_OPERATION_CODE",
    0x182B1E7A: "uOmS204CrouchPoint::cActWait",  # pc-only
    0x182BBC3D: "ROM_BAD_PIPE_FUSE_REG",
    0x182FB9A6: "sRender::HDR_LEVEL",
    0x1832F2D4: "FSB_TX_DEBUG_HI",
    0x1836C1DF: "D1SCL_COEF_RAM_CONFLICT_STATUS",
    0x183788D5: "CCalStream",
    0x18394D02: "VGT_IMMED_DATA",
    0x184218A4: "_DXVA_COPPStatusData",
    0x18425EF2: "_STFC_ALLOCATE_BLOCKS_TYPE",
    0x1846CD4F: "IXUIRuntimeHooks::__vftable",
    0x18496E1E: "CLIPPER_DEBUG_REG00",
    0x184AB4F8: "sPhysics::RigidBody::MyDTI",
    0x184C96EC: "RTS_INV_W_REF",
    0x1857CA8B: "cEm10Action",  # pc-only
    0x185B0EE5: "CLIPPER_DEBUG_REG13",
    0x1867C14A: "cEm84ActReady",  # pc-only
    0x187882E0: "_XMUBYTE4",
    0x187C5A13: "sApp::Item::MyDTI",
    0x187C8069: "D3DXMATRIX",
    0x187D7A92: "D1GRPH_COLOR_MATRIX_COEF_3_3",
    0x18812D80: "std::forward_iterator_tag",
    0x188151B5: "rEffectSetData::RANGE_TYPE",
    0x18819D3A: "rShapeWeight::SHAPE_WEIGHT",
    0x188837D2: "rSoundCurveSetXml::MyDTI",
    0x1888ACAF: "XUINotifyValueChanging",
    0x18892030: "cEm10ActRiseFaceUp",  # pc-only
    0x188D698B: "GPUPRIMTYPE",
    0x188D9868: "CXHttpDownloadBase",
    0x189289FA: "TP1_PERFCOUNTER1_SELECT",
    0x189CC0A2: "_ChexTileInfoStat",
    0x189CD1AB: "FSB_TX_PMC2_AND",
    0x189F88F8: "_XARB_REGISTRANT",
    0x18A359A6: "cEm0bActDieBomb",  # pc-only
    0x18A3AD79: "XPROFILE_ENUM_TITLES_RESULT",
    0x18A795DA: "TICKET",
    0x18A9442A: "uEffectVFR::CHAIN_MODE",
    0x18A9ACE8: "cSetInfoCoord",  # pc-only
    0x18AA3EAC: "uOm095a_Jump::cActPlJump",  # pc-only
    0x18ACB073: "_FILE_MODE_INFORMATION",
    0x18B215AE: "MtString",
    0x18B3C99D: "_ACL",
    0x18B99203: "uEffect2D::__vftable",
    0x18B9C80F: "cEm40ActFarCatchEscape_PL",  # pc-only
    0x18BA1F80: "RB_HSIO_DLL_ADJ0",
    0x18C5505E: "uIdTitle00",  # pc-only
    0x18C65A7B: "_cpinfoexW",
    0x18C82E63: "TP3_CHECKSUM_PIXEL_2",
    0x18CAC372: "_D3DDECLTYPE",
    0x18CB2F19: "cEmc2Action",  # pc-only
    0x18CF02F8: "BSB_WRAPPER_PRBS23_BITCNT0",
    0x18D30341: "PatInterface::Error",
    0x18D5FDD0: "XGI_SESSIONMANAGE_MSG",
    0x18D837C1: "RB_DEPTH_CLEAR",
    0x18DC3B2B: "SQ_INSTRUCTION_CF_ALLOC_2",
    0x18E61E03: "tagEMB_PBMainLoop",
    0x18E7420A: "MtFrustum::HIT_TYPE",
    0x18E87CF1: "sToolBase",
    0x18F55580: "MC0_SECURE_MEMORY_APERTURE_LOG_BIU",
    0x18FB712E: "uEffectEdit::MoveCommon",
    0x18FF2FA6: "cEm84ActDownStripped",  # pc-only
    0x1900CD95: "cEm44ActDamage",  # pc-only
    0x19010956: "MtCollisionGjk::Result",
    0x19018525: "DEPENDENCYREC",
    0x19048BA6: "CP_RT_DMA_SRC_ADDR",
    0x19056E02: "ReadyQCtl",
    0x190B84BB: "_DVD_XGD2_DISC_AUTH_RESULT_INVALID_HV_STATE",
    0x191444E4: "uOmElevator::cActOpen",  # pc-only
    0x1914EBFB: "rEffectSetData::CHAIN_OPTION_FLAG",
    0x191676C6: "D3DQuery",
    0x19202F8C: "SBI_SOFT_RESET",
    0x192212FF: "cEm10ActDmgBody",  # pc-only
    0x1923F802: "cNetEmc3",  # pc-only
    0x1925AB4A: "pDNameNode",
    0x1925EF12: "_CDROM_SEEK_AUDIO_MSF",
    0x19273EEB: "D1SCL_UPDATE",
    0x192BF319: "uModelEdge::EDGE_TYPE",
    0x193286DA: "CP_RT13_BADR",
    0x19343E29: "NetworkRandom",
    0x193A2746: "cScenarioArg_CHP",  # pc-only
    0x193EA064: "uVolumeNoiseFilter",
    0x193FFBB8: "NB_BASE_CODE",
    0x19418433: "DBG_READ_REG",
    0x19474783: "_CERTIFICATE_REVOCATION_BOX_DATA",
    0x1951A775: "MC0_DEBUG",
    0x19542CEB: "cEm22ActRun",  # pc-only
    0x1955176A: "rEffectSetData::ESD_SET_CULL_BILLBOARD",
    0x1955E211: "TP3_PERFCOUNTER0_HI",
    0x1960AC50: "uOmSwitch3::cActMidGrab",  # pc-only
    0x1963734E: "std::reverse_iterator",
    0x19644CC0: "FSB_TLA_TRACE_ARRAY_COUNT",
    0x196FB924: "cEm22ActAtkCutting_PL",  # pc-only
    0x1972E80A: "rMotion::MyDTI",
    0x197A39BF: "SCRATCH_REG7",
    0x198600A2: "_XCONFIG_PLAYTIMERDATA",
    0x1988B1F1: "uOm1303_Truck::cActWait",  # pc-only
    0x19934ACF: "TP0_PERFCOUNTER1_LOW",
    0x1994F9AE: "TP2_CHECKSUM_PIXEL_0",
    0x19964426: "CMdct",
    0x1997A265: "uOma00c_UroAction::cActActorBase",  # pc-only
    0x19985A9D: "PA_SU_PERFCOUNTER0_LOW",
    0x199983FB: "XAUDIOSUBMIXVOICEINIT",
    0x199D3F9B: "_IDEREGS",
    0x19A1048A: "sSoundN::StreamEntry",
    0x19A1AF7F: "HEAP_CATEGORY",
    0x19A5D4EA: "AdjustReconRange_MT_Ctl",
    0x19A8CA37: "FSB_TX_PMC3_OR",
    0x19AB202C: "XConfigSystemSettings",
    0x19AC8C69: "_OBJECT_HEADER",
    0x19ACA8CC: "MtCollada::Shader",
    0x19B087AA: "cPlAction_pl_act_fence",  # pc-only
    0x19BA339B: "MtXmlWriter",
    0x19BA6284: "uOma005_Stairs::cActBase",  # pc-only
    0x19BD59F8: "MtTriangle",
    0x19BEA516: "uModel2Light::MyDTI",
    0x19BF10A5: "D1GRPH_COLOR_MATRIX_COEF_2_3",
    0x19C31E94: "cEm10ActDmgIce",  # pc-only
    0x19C3BA0C: "VGT_DI_SOURCE_SELECT",
    0x19CD1800: "XONLINE_SUBSCRIPTION_CONVERT_MODE",
    0x19CD2BBC: "sPhysics::RigidBodyParam::MyDTI",
    0x19CD6061: "SHORTLE",
    0x19D06B45: "AZ0_COPY_STATE_DWORD1",
    0x19D0A3E8: "FSB_TLA_COUNT0_INIT",
    0x19DBFB09: "XAUDIO::CStereoRoomFloat::__vbtable",
    0x19DC7EC0: "_P_UNBLOCK_MSG",
    0x19DE14B5: "CCalMoviePlayer::__vftable",
    0x19EBCA33: "SQ_INSTRUCTION_ALU_1",
    0x19EC8ECF: "_DVD_XGD2_DISC_AUTH_RESULT_RECALIBRATE",
    0x19ED1C17: "_D3DXSHCOMPRESSQUALITYTYPE",
    0x19F0ADDB: "uBioActorPL00Face",  # pc-only
    0x19F38ECC: "uContrastFilter::MyDTI",
    0x19F99B84: "NetworkCommunity::UserBinary",
    0x19FDF817: "sCapture::SCALE",
    0x19FE9267: "tagOutputType_WMC",
    0x1A0169FF: "uMessage",  # pc-only
    0x1A04E1EC: "cOmHavokAction_dummy",  # pc-only
    0x1A05554C: "uPointLight::MyDTI",
    0x1A09AB7B: "sSoundN::Listening",
    0x1A0BAB1B: "uFreeCamera",
    0x1A0DE7F8: "_SET_ACCOUNT_INFO_REQUEST",
    0x1A0E3E88: "MtGeomPlane::MyDTI",
    0x1A118284: "MC1_WR_STR_DLL_0",
    0x1A12F360: "cOmCoopBoxAction_pl_act_push_loop",  # pc-only
    0x1A156B38: "XAUDIO::CFloatingPointState",
    0x1A173529: "D1CRTC_V_SYNC_A_CNTL",
    0x1A183E3B: "__CrtImplementationDetails::NativeDll",
    0x1A185F6F: "CCalMp2Decoder",
    0x1A19A265: "SCL1_COEFRAM",
    0x1A230419: "_SECURITY_IMPERSONATION_LEVEL",
    0x1A231836: "VGT_PERFCOUNT_SELECT",
    0x1A25FC32: "_P_ADD_2_MSG",
    0x1A30074A: "_SUBSCRIPTION_DETAILS_REQUEST",
    0x1A35855A: "_XMSTV_CREATE_CERTIFICATE_REPLY",
    0x1A36C973: "TYPEENTRY",
    0x1A36EC98: "_I64",
    0x1A3CB1DF: "MtLineSegment",
    0x1A40876F: "PerfEncode",
    0x1A4238B5: "MC1_TUNING_0",
    0x1A4751D9: "FSB_LX_VCARB_AND",
    0x1A4981DB: "rNavigationMeshDae::Mesh",  # pc-only
    0x1A4CBF13: "SQ_FLOW_CONTROL",
    0x1A50EE30: "uOmLaserMirror::cActPlCatch",  # pc-only
    0x1A526BCA: "uEffectVFR::CLOTH_STATUS",
    0x1A541082: "cEm10ActDmgFire",  # pc-only
    0x1A57B9F2: "LMSPredictor",
    0x1A5EE859: "rEffectList::VIB_REQ_TYPE",
    0x1A5FCDCC: "sApp::Item::TYPE",
    0x1A601306: "_PM4CMDIMLOADIMMEDIATE",
    0x1A642EE3: "D3DCubeTexture",
    0x1A644532: "_XACTIVATION_TITLE_LICENSE_INFO",
    0x1A6E6A33: "rSoundSpeakerSetXml::DirectionalCurve",
    0x1A714F97: "_FloatOutStruct",
    0x1A752A41: "cEm30ActDmgDieExplosion",  # pc-only
    0x1A77E719: "PIX_REQUEST_MODE",
    0x1A79E60D: "_BANNER_HOTLIST_RESULT",
    0x1A8E0469: "cShape",
    0x1A8F6787: "_XUSER_STATS_COLUMN",
    0x1A91F587: "PA_CL_GB_VERT_CLIP_ADJ",
    0x1A9489A0: "FSB_LX_PHYDATA",
    0x1A9BE91A: "_XCONFIG_XNET_ENTRIES",
    0x1A9CB9CC: "_XUSER_PLAYERLIST_INTERNAL",
    0x1A9F2E54: "PROCMODE_ID",
    0x1A9FC20E: "cAIFSM::Transition",  # pc-only
    0x1AA27B3B: "cPlAction_pl_act_attack_finish_2",  # pc-only
    0x1AA68BBE: "FSB_TX_TERST_XSTP_OR",
    0x1AA6F1BE: "cEm84ActPinionedAtk",  # pc-only
    0x1AA9B119: "rSoundSpeakerSetXml::SpeakerSet",
    0x1AAC5065: "cTrans::Technique::FUNCTION",
    0x1AAF9932: "cMaterial::BLEND",
    0x1AB029F5: "_FILETIME",
    0x1AB34F20: "cPlAction_pl_act_avoid_left",  # pc-only
    0x1AB3C319: "cEm44ActGetup",  # pc-only
    0x1AC09ADD: "CP_RT1_SIZE",
    0x1AC553A3: "_DM_ODD_SPINDLE_SPEED_CHANGE_DATA",
    0x1AC6BEA9: "CP_RT2_POLL_ADDRESS",
    0x1ACB9701: "cFSMOrder::FuncParamFreeF",  # pc-only
    0x1AD0DA8F: "sSoundN::VOICE_CATEGORY",
    0x1AD289D3: "TCF_PERFCOUNTER9_SELECT",
    0x1AD8D8E7: "r2Texture::HEADER2",
    0x1ADBE7D3: "cEm83ActDmgGetup",  # pc-only
    0x1ADC9D85: "cEm10ActAtkDashBomb",  # pc-only
    0x1AE39E0A: "ColorformatX",
    0x1AE4CE8A: "std::basic_string",
    0x1AE89B40: "cPlAction_pl_act_wait",  # pc-only
    0x1AF2C39F: "_XCONFIG_XNET_SETTINGS",
    0x1AF46990: "MtCollisionGjk",
    0x1AF7C4ED: "PROCMODE",
    0x1AF83E50: "rSoundDirectionalSetXml",
    0x1AFE912A: "cWpAction_wp_act_ready_begin",  # pc-only
    0x1AFFF120: "HINSTANCE__",
    0x1B02F66C: "cEm4502ActAppear",  # pc-only
    0x1B061B6E: "sLightLinker::Camera",  # pc-only
    0x1B0D4A33: "_XMSG_DOWNLOAD_ATTACH_TO_MEM_PARAMS",
    0x1B0DDA6E: "FSB_TR_DEBUG_LO_OR",
    0x1B0E1839: "CXCabCryptHelper",
    0x1B137961: "TCF_PERFCOUNTER5_LOW",
    0x1B16D795: "_CACHEHASHTABLEENTRYBLOCK",
    0x1B170C5D: "_PM4CMDINVALIDATESTATE",
    0x1B1D6272: "D1CRTC_INTERLACE_STATUS",
    0x1B254793: "FSB_LR_DEBUG_HI",
    0x1B2A37FA: "cTrans::CMD_CLIPPLANE",
    0x1B2D8AB4: "TCB_FETCH_GEN_PIPE1_DEBUG",
    0x1B3AD15B: "_XPROFILE_SYNC_TITLES_REQUEST",
    0x1B3B8BD0: "cEm84ActRollFire",  # pc-only
    0x1B4162D4: "_RTL_HEAP_ENTRY",
    0x1B41B146: "cPlAction_pl_act_attack_add_mouse",  # pc-only
    0x1B424E05: "_XPROFILE_ACHIEVEMENT_SYNC_REQUEST",
    0x1B435412: "CP_DMA_ACT_DSCR_STAT",
    0x1B4BD3D8: "_D3DLOCKED_RECT",
    0x1B585399: "MtCollada::Extra",
    0x1B5C522A: "PERSTREAMSTRUCT",
    0x1B5DE219: "SECONDARY_STATUS",
    0x1B5E5B80: "XUIMessageDisableFocusRecursion",
    0x1B5EB084: "cPlAction_pl_act_weapon_ready_begin",  # pc-only
    0x1B60C64D: "uToneCurveFilter::MyDTI",
    0x1B626823: "DC_LUTA_WHITE_OFFSET_GREEN",
    0x1B62FF7F: "XONLINE_PAYMENT_INSTRUMENT_TYPE",
    0x1B6A266D: "sMain::JOB_MODE",
    0x1B747CD9: "_P_ADD_AFFILIATES_MSG",
    0x1B7CADF8: "CP_CPU_INT_STATUS",
    0x1B7FAF9D: "cEm44ActAtckDive",  # pc-only
    0x1B85C8B7: "uEffectVFR::Hit",
    0x1B86375C: "CCalChannel::__vftable",
    0x1B870E3C: "_MIGRATE_XBOX_COM_USER_RESPONSE",
    0x1B8A307C: "BASE_CODE",
    0x1B8AC180: "VGT_PERFCOUNTER0_SELECT",
    0x1B8DFF77: "sPrim::DepthOrder",
    0x1B938AAC: "cShape::ATTR",
    0x1B96BCF1: "cMaterialStandard::FUNC_NORMALMAP",
    0x1B96F13B: "MtCollada::Sampler",
    0x1BA342D7: "PACKET_BUFFER",
    0x1BA5750D: "XUIRenderStats",
    0x1BAA5612: "cPlAction_pl_act_attack_lariat_uro_b",  # pc-only
    0x1BB83479: "_RECORDTABLEOFFSETENTRY",
    0x1BBB1E19: "D3D::CValidatePacket",
    0x1BC33C8E: "BufFilt",
    0x1BC760C7: "uEffectVFR::MoveAdd",
    0x1BCC4966: "rSoundRequest",
    0x1BD27330: "FSB_TX_CMDMM0_AND",
    0x1BD27453: "D1GRPH_SURFACE_OFFSET_X",
    0x1BD81FDC: "_UPDATE_ACCESS_TIMES_REQUEST",
    0x1BDE0307: "cNetEm42",  # pc-only
    0x1BE2EEED: "uFlowingWater",
    0x1BED9E24: "rSoundSpeakerSetXml::SPEAKER_SETTING",
    0x1BEF6843: "NetworkQueue::Buf",
    0x1BF767A9: "XUIMessageGetTeletypeMax",
    0x1BF8224E: "cFSMOrderElevator::FuncParamElevatorSet",  # pc-only
    0x1BF9AEFC: "D1GRPH_COLOR_MATRIX_COEF_1_3",
    0x1BFCAFA9: "_PRIVILEGE_SET",
    0x1BFE6EC1: "sSoundN::Voice::__vftable",
    0x1C06A3E2: "_XNPGREYLISTADDRESSES",
    0x1C120BBF: "GPUFrameRenderInfo",
    0x1C149EBF: "MtFCurve::Key::MyDTI",
    0x1C1652FB: "cTrans::CMD_PROFILE::MODE",
    0x1C16FF5C: "_XSTAT_PROC_PARAM",
    0x1C17ACD4: "cFSMOrderPlayer::FuncParamMuteki",  # pc-only
    0x1C1A09BE: "_KQUEUE",
    0x1C1A38EA: "_TRACK_MODE_TYPE",
    0x1C1E81DF: "D1MODE_VBLANK_VLINE_STATUS",
    0x1C224145: "cPlAction_pl_act_coop_jump_up_4m_jump",  # pc-only
    0x1C22F835: "tagWMVDecodeDispRotateDegree",
    0x1C2E1EAD: "sCollision::TYPE",
    0x1C300B04: "CCalBase::PLAY_FLAGS",
    0x1C3336E9: "FSB_TX_CTRL",
    0x1C33A80E: "cEm10ActDeadFaceUpPF",  # pc-only
    0x1C33CB09: "uCuboidShadowLight::MyDTI",
    0x1C3C4EBD: "FSB_LX_LSPARE_AND",
    0x1C3EC884: "FSB_TLA_COMPR_CARE_MASK3",
    0x1C40922D: "TP0_CHECKSUM_PIXEL_0",
    0x1C4138EE: "MtDataWriter",
    0x1C415D6B: "cAIFSM::ParamBitFlag32",  # pc-only
    0x1C42B895: "uOmJeep::cActPlRide",  # pc-only
    0x1C446AD8: "NetworkLayer::FilterList",
    0x1C45722B: "HDCP_STATUS_CODE",
    0x1C47214C: "TP2_PERFCOUNTER1_LOW",
    0x1C486AFD: "_XC_PASSKEY",
    0x1C48B10D: "D1MODE_VBLANK_STATUS",
    0x1C4CF7D4: "uOmCrank::cActRewind",  # pc-only
    0x1C4D2277: "XSVSESSION",
    0x1C50833E: "rConfig::DATABASE",
    0x1C54E873: "CP_RT2_SIZE",
    0x1C555BDE: "RB_HSIO_ROUNDTRIP_LATENCY",
    0x1C6458F7: "XGI_PREPAREGAMERTILES_MSG",
    0x1C648565: "AZ1_MRT_STATE_DWORD1",
    0x1C692C1C: "PatInterface::LayerUserNtc",
    0x1C723289: "uOm0944::cActWaitToUp",  # pc-only
    0x1C74DDCB: "XGI_SESSIONMODIFY_MSG",
    0x1C75DB9F: "MtFloat2",
    0x1C7BB4D4: "_DM_COUNTDATA",
    0x1C7C9B08: "sNetwork::MyDTI",
    0x1C81A3D4: "uOmFollow::cActWait",  # pc-only
    0x1C82C034: "VGT_PERFCOUNTER3_LOW",
    0x1C860727: "MtVirtualAllocator::MyDTI",
    0x1C86562E: "cTrans::CMD_PRIM",
    0x1C8837AC: "XAUDIO::CMasterMemoryManager",
    0x1C88DDA8: "rVibration::VIB_PAD_SINGLE",
    0x1C8B3C6D: "rAIFSM::ParamConstF32",  # pc-only
    0x1C8D7CD7: "UVBASE_ENUMERATECHANNELSPARAM",
    0x1C8D8BC4: "_XEX_TLS_DATA",
    0x1C8E625B: "cWpAction_wp_act_wait",  # pc-only
    0x1C8F4B96: "_xDISPATCHER_CONTEXT",
    0x1C922872: "cOmRider2ActDmgFlyoff",  # pc-only
    0x1C93D346: "aColorBar",  # pc-only
    0x1C95E43E: "rSoundSource::SAMPLELOOP",
    0x1C99A409: "uDirectionalGlowFilter::MyDTI",
    0x1C99B518: "XIPTV_DVR_STATUS_FLAGS",
    0x1C9BA495: "MtArray::MyDTI",
    0x1CA0812E: "XAUDIO::CPCMSourceEffect::__vftable",
    0x1CA0E3D9: "rEffectList::PLACE_TYPE",
    0x1CA264E0: "PIXMetaClearData",
    0x1CA7273C: "_TRANSFER_MACHINE_LICENSES_REQUEST",
    0x1CA7F29C: "MtAllocator::ATTR",
    0x1CA89812: "SBR_ERROR",
    0x1CA9E6F4: "uSoundSe",  # pc-only
    0x1CAEE7D8: "SQ_PERFCOUNTER1_SELECT",
    0x1CB05B27: "IXHVEngine::__vftable",
    0x1CB3C71E: "cNetEm46",  # pc-only
    0x1CB705CB: "ID3DXFragmentLinker::__vftable",
    0x1CBCA703: "sPrim::LAYOUTMODE",
    0x1CBF6F04: "NEWINDEXBLOCKS",
    0x1CCAFFF8: "rSoundSourceXMA::XMA2WAVEFORMAT_OLD",
    0x1CCB5BE1: "_PURCHASE_OFFERS_REQUEST",
    0x1CCC1FA1: "uChainEx",  # pc-only
    0x1CCE0B7A: "CRTC_DOUT_INTERFACE_01_DEBUG",
    0x1CD0E1D1: "cEm60ActWait",  # pc-only
    0x1CD3870C: "D3D::MajorMode1PrimRegs",
    0x1CDB4D00: "D1CRTC_V_BLANK_START_END",
    0x1CE02975: "TCO_QUAD1_DEBUG1",
    0x1CEBEC6A: "sPrim",
    0x1CF0AA99: "GPUCmdRepeatpad",
    0x1CF2267F: "cEm20ActTurn",  # pc-only
    0x1CF2573A: "sCamera::Viewport::MyDTI",
    0x1CF29E9A: "cMaterial",
    0x1CFE224B: "cScenarioArg_Note",  # pc-only
    0x1D0196CB: "TPC_DEBUG1",
    0x1D043761: "sArea::AreaInfo::MyDTI",
    0x1D080075: "cEm30PlEvent_NeckBiteHitTH",  # pc-only
    0x1D098CDE: "_UCODE_DEFINITION_TABLE_MASKEDSTATEDELTA",
    0x1D0D119A: "cFSMOrder::FuncParamBattleBGM",  # pc-only
    0x1D11DFA3: "uOmSwitch3::cActMidRelease",  # pc-only
    0x1D19310F: "uOmCrank::cActPlBase",  # pc-only
    0x1D1B54C0: "IOC_TST_MODE_ENABLE",
    0x1D1C45E0: "TP1_CHECKSUM_PIXEL_2",
    0x1D1E5F1B: "cEm40ActNearCatchOk",  # pc-only
    0x1D203331: "IPersist::__vftable",
    0x1D21D7C8: "sRender",
    0x1D2681DC: "t_LocalHuffmanDecoder",
    0x1D26F42D: "cEm10ActAtkPlagaRand",  # pc-only
    0x1D27F45C: "PA_CL_VPORT_XOFFSET",
    0x1D2A552E: "CP_RT_ME_RAM_WADDR",
    0x1D2AA163: "rEffect2D::FLAG32",
    0x1D2B18EE: "RB_STENCILREFMASK_BF",
    0x1D2BC050: "_DMDVD",
    0x1D3424F8: "XAUDIO::SRC::LinearVector",
    0x1D3596FF: "cOmRollAction_wait",  # pc-only
    0x1D3733E0: "MH_INT_STATUS",
    0x1D39BB11: "CArgumentList",
    0x1D3B8A29: "tagCPanScanInfo",
    0x1D3CC42D: "CBitStream::__vftable",
    0x1D40CE8C: "ID3DXFileData::__vftable",
    0x1D43E0CE: "XCOMPRESS::LDI_CONTEXT",
    0x1D47DFC3: "PCIE_PERF_LATENCY_THRESHOLD",
    0x1D47E3AD: "XGCpuShaderDevice",
    0x1D4D1715: "XECRYPT_SIG",
    0x1D549BEA: "XUI_SMOOTHSCROLL_ORIENTATION",
    0x1D5E2DD2: "PARSERINSTANCE",
    0x1D62DCA1: "_XARB_REPORT_BYTE_BUNDLE",
    0x1D62DCFB: "cPlAction_pl_act_attack_knee_bazooka_turn_l",  # pc-only
    0x1D680B78: "NetworkSessionManagerLive::QOS_FOR_MEMBER",
    0x1D6C121A: "_XONLINE_QUERY_ATTRIBUTE",
    0x1D6CA000: "_FILE_ALLOCATION_INFO",
    0x1D6DAE00: "_XRESOLVE_DOMAIN_STRING",
    0x1D6EA2F2: "IPersistStream::__vftable",
    0x1D6F62FD: "cEm8cActEvent",  # pc-only
    0x1D729205: "cEm0cActReadyBgn",  # pc-only
    0x1D7B4BC4: "uBioBlurFilter",  # pc-only
    0x1D7BDE16: "AZ0_LOOPBACK_PATTERN0PHS2",
    0x1D7D71AB: "MSI_MSG_DATA_64",
    0x1D7DA970: "MtMemoryStream::MyDTI",
    0x1D8042A7: "PG_START",
    0x1D83AD01: "cEm0cActReady",  # pc-only
    0x1D853F6D: "cEm41ActDiscloseLoop",  # pc-only
    0x1D8719C5: "XGI_RECOVERTITLE_MSG",
    0x1D8DD429: "CCalAudioRenderer",
    0x1D915274: "XUIMessageDeleteText",
    0x1D928118: "RS2StageVQ_MBlk",
    0x1D9FE9B9: "PACKETSTATE",
    0x1DA4BE42: "cScenarioData",  # pc-only
    0x1DA7DB4C: "localeinfo_struct",
    0x1DAD9AD1: "MARKERENTRY",
    0x1DAF24F8: "rEffectList::EFL_LIFE_FRAME",
    0x1DB7F3BE: "NetworkResolver",
    0x1DB93139: "uOmSwitch::cActWaitToOff",  # pc-only
    0x1DBA09D7: "MtCollision::SimplexSolver::__vftable",
    0x1DC1287C: "cEm3403ActErase",  # pc-only
    0x1DC52A5C: "uOmUseItem::cActNoItem",  # pc-only
    0x1DC99DDD: "_DVD_XGD2_DISC_AUTH_RESULT_GET_XCONTROL",
    0x1DCA5BF4: "_HAL_SMC_REGISTRATION",
    0x1DD1269C: "_XUSER_READ_PROFILE_SETTING_RESULT",
    0x1DD4E12D: "AACAudioDecoderInitializationOptions",
    0x1DD5DCA3: "cLinkUnit",  # pc-only
    0x1DD8F5E2: "BRTLOCALBUFFERSTATE",
    0x1DE1DE01: "_XMBYTEN4",
    0x1DE8AC23: "sApp::Item::__vftable",
    0x1DEB5103: "MtGeomAABB::AABB_VORONOI_ID",
    0x1DEFBA60: "PIX_CHUNK_LOCATION",
    0x1DF09DD8: "decoder_state",
    0x1DF5DBDC: "VGT_DI_MAJOR_MODE_SELECT",
    0x1DFCAB24: "_XCONTENT_DATA_INTERNAL",
    0x1E00E7C5: "uOma00c_UroAction::cActActorAB",  # pc-only
    0x1E063692: "ID14_BLEND_DATA_G",
    0x1E06E4FE: "MtPhysicalAllocator::__vftable",
    0x1E07882D: "D3DXQUATERNION",
    0x1E0B889B: "NMCodecPerfStruct",
    0x1E0D0128: "FSB_LR_DEBUG_HI_OR",
    0x1E11212B: "cEm6cActErase",  # pc-only
    0x1E13B364: "_XTDECODER_PARAMETERS",
    0x1E15E378: "cOmBreakAction_base",  # pc-only
    0x1E1765E0: "FSB_TLA_TRACE_ARRAY_DATA3",
    0x1E17FDA6: "SCRATCH_REG3",
    0x1E1B0764: "GC_LATENCY",
    0x1E1B90F1: "REGPROG_INF",
    0x1E1C537F: "_ACCOUNT_LINK_XBOX1_ACCOUNT_REQUEST",
    0x1E2943CF: "ID3D10Texture2D",
    0x1E294F48: "_STRING32",
    0x1E2A4415: "_LOGON_CHECK_REQUEST",
    0x1E2F9B0F: "CP_RT12_REFERENCE",
    0x1E30CE50: "DC_LB_MEM_SIZE",
    0x1E31632B: "_s_HandlerType",
    0x1E325296: "CMarshaller",
    0x1E358FCB: "cEm84PlEvent_PinionDmg",  # pc-only
    0x1E35F38B: "_XCONTENT_SIGNATURE_TYPE",
    0x1E3722BC: "EP_BASE_CODE",
    0x1E434BB6: "_XINPUT_STATE",
    0x1E44E91C: "TCF_PERFCOUNTER11_HI",
    0x1E4C067C: "_XMFLOAT4",
    0x1E55329E: "cEm8cAtkTornado",  # pc-only
    0x1E579C47: "sNetworkLibraryXbox",
    0x1E6161D9: "cOmContainerAction_base",  # pc-only
    0x1E65D0C4: "CP_RT7_POLL_ADDRESS",
    0x1E6C67E8: "XDVO_FORCE_DATA",
    0x1E6C772B: "MtCollada::Matrix",
    0x1E6D148D: "MC0_TIMING_CNTL_2",
    0x1E722561: "uEffectEdit::Billboard",
    0x1E73BA03: "MOTION_INFO",
    0x1E73EABB: "uOm1303_S109_Truck::cActBarricade",  # pc-only
    0x1E7B7C0E: "rSoundStreamRequest::SOUND_STREAM_REQUEST_EQ_CATEGORY",
    0x1E7E29DA: "PatInterface::FoItem",
    0x1E850E5D: "uOm0892_Lift::cActWait",  # pc-only
    0x1E87F30F: "D1CRTC_STATUS_HV_COUNT",
    0x1E8D6161: "sMain::PROCESS",
    0x1E918602: "uOmKickSwitch::cActBase",  # pc-only
    0x1E943E39: "tagWMA_StreamPayloadExtensionData",
    0x1E96365F: "rEffectSetData::ESD_MOVE_PATH_KEYFRAME_COLL",
    0x1E9FAB1A: "CXuiListItem",
    0x1EAC34D9: "RTS_EDGE_2_DX",
    0x1EAD1445: "XMEDIA_STREAM_ID",
    0x1EAE7478: "cNetPlayer",  # pc-only
    0x1EAF8793: "cPlAction_pl_act_avoid_right",  # pc-only
    0x1EB174E5: "NetworkSession::__vftable",
    0x1EB28179: "CXContentDownloadMedia::REFRESH_LICENSE_RESPONSE_BUFFER",
    0x1EB2DBA7: "uOmCoopSwitch_S301::cActOpened",  # pc-only
    0x1EB35ABF: "cFSMOrderDoor::FuncParamDoorSet",  # pc-only
    0x1EB8675A: "_XUSER_SIGNIN_INFO",
    0x1EC3828B: "D3D::CPerfCountersPhysical",
    0x1EC3AC72: "PatInterface::UserNtc",
    0x1EC7E838: "cAIBlackBoard::WriteContainer",  # pc-only
    0x1EC9902C: "uModelSky",
    0x1ECB1AB6: "std::num_get",
    0x1ECBA1EE: "NB_HEADER",
    0x1ECFAEB5: "D3DDevice",
    0x1ED12F1B: "rGoalPos",  # pc-only
    0x1ED4C527: "D3D::SegmentCallNode",
    0x1ED6130F: "DCCG_ONE_SHOT_RUN_CLOCKS_COUNT",
    0x1ED7AB99: "SB_COMMAND",
    0x1EDD90FA: "rSoundStreamRequest::WriteHeader",
    0x1EDEE66C: "DC_SURFACE_2_EXTENT",
    0x1EE199FE: "rTexture::SHFACTOR",
    0x1EE58B80: "_TOKEN_PRIMARY_GROUP",
    0x1EEA3D22: "_XNPROUTEENTRY",
    0x1EF32952: "TP2_PERFCOUNTER0_HI",
    0x1EF33611: "cPlAction_pl_act_attack_knife_flying",  # pc-only
    0x1EF4DF5C: "cEm70ActBox",  # pc-only
    0x1EF70CEA: "cOmCoopBoxAction",  # pc-only
    0x1EFB1B67: "rAdhesion",  # pc-only
    0x1EFB9326: "FSB_LX_DEBUG_AUX_OR",
    0x1EFE1FDF: "MP4TrackAtom",
    0x1EFFDE2B: "NetworkCommunity::Friend",
    0x1F016578: "AZ1_LOOPBACK_PATTERN0PHS1",
    0x1F15828E: "_XMXICON4",
    0x1F192715: "MtStream::SEEK_ORIGIN",
    0x1F24AA07: "CLIPPER_DEBUG_REG04",
    0x1F2D1EBC: "_D3DXCONSTANTTABLE_DESC",
    0x1F3422D8: "MtFileStream",
    0x1F3463CE: "_KUSER_MODE_PAGE",
    0x1F44D146: "FSB_TLA_COUNT3_INIT",
    0x1F459F32: "sSoundN::PAUSE_STATUS",
    0x1F46601D: "uToneMapFilter::GhostDef",
    0x1F47EB23: "_D3DDECLMETHOD",
    0x1F4865D2: "cEm42CActBreak",  # pc-only
    0x1F493E03: "rEffect2D::E2D_KEYFRAME_F32",
    0x1F4BE986: "MtTime",
    0x1F4D3CF0: "CHuffmanTable",
    0x1F4D585D: "_HV_PAGE_INFO",
    0x1F54ABD1: "uOm08e3_RuinTrap::cActWait",  # pc-only
    0x1F5515FE: "sCollision::HIT_TARGET",
    0x1F58BC68: "cEma2ActSyoteOk_PL",  # pc-only
    0x1F5919D7: "cEm65ActErase",  # pc-only
    0x1F6E0196: "_CEA861_TIMING_EXTENSION",
    0x1F6FE0D4: "cEm84ActReadyRoll",  # pc-only
    0x1F701C3E: "TST_EDGE_DETECT_CONTROL",
    0x1F715EFC: "VGT_HOS_CNTL",
    0x1F71A43A: "PatInterface::KickOption",
    0x1F72A335: "IXHVExternalCodecVtbl",
    0x1F775F2D: "FSB_LX_PHYCMD",
    0x1F789FCB: "_XSIGNATURE_CHECK_REVOCATION_RESPONSE",
    0x1F7A52FA: "_D3DXKEY_QUATERNION",
    0x1F7BE34E: "GPUCOPYSAMPLESELECT",
    0x1F7F0748: "_XCONTENT_REFRESH_LICENSE_RESPONSE",
    0x1F7F10B6: "sPad::Pad::MyDTI",
    0x1F7F23AE: "cPlAction_pl_act_wall_crouch_off",  # pc-only
    0x1F82B805: "uEffectVFR::LensFlare",
    0x1F840394: "RecordRestore",
    0x1F8530A1: "FnTableInterp",
    0x1F862C07: "GPUCmdCopyBuffer",
    0x1F869FD4: "rEffect2D::E2D_MOVE_MUL",
    0x1F90FAC2: "_FPSCR",
    0x1F9CB941: "CP_PFP_UCODE_ADDR",
    0x1FA1B228: "__VECTOR_PACK_MASK",
    0x1FA6F474: "CP_RT10_BADR",
    0x1FAA26A5: "IXUIPropObj::__vftable",
    0x1FAF190B: "_flt",
    0x1FB0AF8B: "sPrim::Prim::METADATA_TYPE",
    0x1FB12456: "_XGI_VIEWRESET_MSG",
    0x1FB81588: "cFSMOrder::FuncParamApplyPos",  # pc-only
    0x1FBE1059: "MtBlockAllocator",
    0x1FC5FB7E: "SQ_RESOURCE_MANAGMENT",
    0x1FD72C35: "sSoundN::STATUS",
    0x1FD7DB99: "RB_HSIO_DLL_ADJ4",
    0x1FDA696D: "_PROXY_CLASS",
    0x1FDA83D2: "FrameType",
    0x1FDAFBAB: "cEm43ActHookB",  # pc-only
    0x1FDBF9B5: "uShadow",
    0x1FDDBD73: "MtGeomMinkowskiSum::MyDTI",
    0x1FDE0F0B: "CP_RT_BIN_MASK_HI",
    0x1FDF3F2D: "cTrans::CMD_CLEARHS",
    0x1FE06AFE: "AZ1_RESET_CRC_COUNTERS",
    0x1FE95F01: "uEffect2D::MoveNone",
    0x1FE9C295: "_XMUDHEN3",
    0x1FEBE170: "_D3DVIDEO_SCALER_PARAMETERS",
    0x1FF17C2B: "BIOS_11_SCRATCH",
    0x1FFE3A79: "ID3DXEffectCompiler::__vftable",
    0x20038ECE: "HSIO_DLL_ADJ4",
    0x200574C1: "RBBM_ISYNC_CNTL",
    0x20069762: "GetMoreDataMode",
    0x200FD21D: "PA_CL_UCP_0_Y",
    0x2011A60F: "_D3DTRIPATCH_INFO",
    0x2015F77B: "CP_RT5_REFERENCE",
    0x201AE146: "CP_BIN_MASK_HI",
    0x201BF7A6: "AZ0_LOOPBACK_PATTERN1PHS2",
    0x201D8B72: "_FXLSAMPLERSTATEENTRY",
    0x2027CD09: "cEm84ActWalk",  # pc-only
    0x202C1E35: "_ACCOUNT_CHANGE_GAMERTAG_RESPONSE",
    0x20360442: "sSoundN",
    0x20389373: "XUIMessageWantFocus",
    0x204159B9: "NetworkPeerMcs",
    0x2046C6D4: "TCM_CHICKEN",
    0x204D4521: "_FILEEVENTVIEWERCALLS",
    0x204D6AAB: "PIX_RECORD_VIDEO_FRAME",
    0x205072C4: "sLightLinker::EffColor",  # pc-only
    0x2051FB2A: "_XMATCH_SEARCHRESULT_HEADER",
    0x205739C8: "sEventPlayer::cEventActionButton",  # pc-only
    0x20584856: "_P_INVITATION_ANSWER_ITEM",
    0x2058D194: "D3D::SegmentCall",
    0x20593DB6: "MtPhysicalAllocator::ATTR",
    0x205AB3AA: "UVBASE_QUITVOICECHATPARAM",
    0x205BD661: "_XUSER_STATS_READ_RESULTS",
    0x205FEB12: "cEmc4ActWait",  # pc-only
    0x206190F2: "cEm8cAtkShield",  # pc-only
    0x2061A00E: "uOmElevator::cActEvEmSet",  # pc-only
    0x2063703B: "rEffectStrip::MyDTI",
    0x206E1D78: "MtGeomMinkowskiDiff",
    0x206FEB7B: "cOmRollAction_base",  # pc-only
    0x2077F6A8: "uOma004_Collapse::cActStart",  # pc-only
    0x207830B9: "IXAudioEffectVtbl",
    0x207A0CBE: "_P_PEER_SESSION_MSG",
    0x207C2903: "cEm10ActAtkFatHandPunch",  # pc-only
    0x207DDF6A: "uOma00c_UroAction::cActEnd",  # pc-only
    0x208242AE: "_PERFPIPE_TRANSFER_LENGTH_INFORMATION",
    0x2085CF5E: "tagWMAFileVersion",
    0x208643CE: "cEm41ActBeatDownB",  # pc-only
    0x208821B0: "_XSHOWMARKETPLACEDOWNLOADITEMSUI_ENTRYPOINTS",
    0x20886D53: "FSB_TLA_CONDITION1",
    0x208C3700: "_XONLINE_TEAM_MEMBER",
    0x208E873F: "PA_CL_GB_HORZ_CLIP_ADJ",
    0x20948E5A: "cEm84PlEvent_DownStripDmg",  # pc-only
    0x20960DAF: "CARDEA_CSP_INTERFACE_IMP::CARDEA_CSP_PARAMS",
    0x2096388C: "cEmc0ActBreak",  # pc-only
    0x209A5078: "uEffectEdit::PrimModelKeyframe",
    0x209B33D5: "XUIMessageRender",
    0x20A81BF0: "rAIPositionEvaluationFuncList",  # pc-only
    0x20A88B08: "sCollision::cSbcArrayBP::MyDTI",
    0x20A8ADAE: "HWINEVENTHOOK__",
    0x20ADE181: "_XPROFILE_SYNC_ACHIEVEMENTS_RESULT",
    0x20AE0D01: "Sample_Cntl",
    0x20AF8FC4: "_XMHEND3",
    0x20B7EC00: "CCalSyncMemoryQueue",
    0x20B8D4A9: "XUIElementPropVal",
    0x20B9BADA: "CP_RT13_MASK",
    0x20BCB37A: "_XMSG_DETAILS_INTERNAL",
    0x20BDA988: "uOm08db::cActExplode",  # pc-only
    0x20BFDFA8: "MC_PERFCNT_SELECT",
    0x20C168FA: "rCollision::PartsInfo",
    0x20C7B287: "uFSMTask",  # pc-only
    0x20C9EC94: "_PROCESS_HEAP_ENTRY",
    0x20CADFFC: "cEm45ActAttack",  # pc-only
    0x20CDCAD9: "_KTHREAD",
    0x20CE7EF0: "cEm6fActFreeFly",  # pc-only
    0x20CE8FEA: "_XARB_REGISTER_REPLY",
    0x20D594E9: "_MESSAGEBOX_PARAMS",
    0x20DA0C63: "CHuffmanBitObj::__vftable",
    0x20DDB072: "_COPP_BusType",
    0x20E317CE: "PCIE_TX_REQUEST_NUM_CNTL",
    0x20EEECFA: "XUIRenderStruct",
    0x21026FE4: "cPlAction_pl_act_avoid_crouch",  # pc-only
    0x2108D589: "_D3DXINCLUDE_TYPE",
    0x210A5C46: "_XEX_COMPRESSED_DATA_DESCRIPTOR",
    0x210C227E: "_PASSPORT_GET_ENCRYPTED_PROXY_PARAMETERS_REQUEST",
    0x210C9AB9: "_Q_MESSAGE_SUMMARY_REPLY_MSG",
    0x210EE8B1: "CP_RT15_COMMAND",
    0x210F483D: "_XONLINE_MATCH_SEARCHRESULT",
    0x21101E26: "ID3DXCompressedAnimationSet",
    0x2114AD52: "FSB_TX_PMC2_OR",
    0x2118926F: "CCalOverlappedIoBlock::__vftable",
    0x2119A4FE: "PatInterface::FoBinary",
    0x2123D97A: "MtCollada::Geometry",
    0x2123DD4A: "_DMGD",
    0x2125EBA7: "OperandSelect1",
    0x2126DF51: "XNetConfigParams",
    0x212708FC: "TP2_PERFCOUNTER0_LOW",
    0x212715E6: "_RECOVER_ACCOUNT_RESPONSE",
    0x212731AE: "PA_SU_POLY_OFFSET_FRONT_SCALE",
    0x212766A0: "XECRYPT_DH_768",
    0x212B0F34: "cEm22ActAtkTurnCut",  # pc-only
    0x212CADA3: "cEm10ActAtkSpearBig",  # pc-only
    0x21332E69: "AHEffectColor",  # pc-only
    0x21351A26: "DO_TEST_DEBUG_EDGE_TRIGGER_PATTERN",
    0x21359C2A: "sCollision::Sbc",
    0x21362CB5: "cOmJeepAction_om_act_damage_yoro",  # pc-only
    0x21365D9C: "DCCG_ONE_SHOT_RUN_CLOCKS_CNTL",
    0x2136F149: "XAUDIO::CPCMSourceEffect",
    0x213A2B27: "stdext::exception",
    0x21416F1C: "cEffectAnim",
    0x2145DCAA: "MOTION_PARAM",
    0x21479E6C: "cEm32ActAtkMount",  # pc-only
    0x2147D192: "uOm092e_LaserBlock::cActReady",  # pc-only
    0x2148845B: "NetworkRankingLive",
    0x2149F9DA: "uOm0933::cActExplode",  # pc-only
    0x214BD5D2: "_XARB_REGISTER_REQUEST",
    0x2152BC48: "FSB_TX_DEBUG_LO_OR",
    0x21563655: "IXAudioEffectManager",
    0x2156504B: "NetworkBuffer::__vftable",
    0x21594C82: "VGT_DMA_DATA_FIFO_DEPTH",
    0x215B9618: "XUISubtimelineData",
    0x215DABC2: "rEffectSetData::FORCE_TYPE",
    0x2162836B: "rHavokVertexLayout::LayoutInfo",  # pc-only
    0x216392F3: "_ACCOUNT_ACKNOWLEDGE_DOWNGRADE_REQUEST",
    0x21641FCB: "_MSR",
    0x2164581B: "rSoundStreamRequestXml::MyDTI",
    0x21695CA6: "PAYLOADPARSEINFO",
    0x216FB845: "ID3DXSkinInfoVtbl",
    0x217162D7: "sRender::Pass::FILL_MODE",
    0x21736AD6: "FRAME_JUMP_UNWIND",
    0x21741A72: "D3DXVECTOR4_16F",
    0x217BF7F0: "XONLINE_CONTENT_HISTORY_INFO_FLAGS",
    0x217EE43F: "XNDNS",
    0x217EFA31: "CP_MEQ_STAT",
    0x2181FB76: "_XREVOCATION_VERIFY_PARAMS",
    0x2187E08C: "cPlAction_pl_act_wall_stick_t_ready_weapon_direct",  # pc-only
    0x2187FA78: "MaskStyle",
    0x2189FF14: "cEm80ActNeeOk_PL",  # pc-only
    0x218C1272: "SQ_INSTRUCTION_CF_EXEC_2",
    0x218F456D: "_SUBSCRIPTION_DETAILS_RESPONSE",
    0x21924E76: "cEm3403ActWait",  # pc-only
    0x21936B12: "_XUSER_CONTEXT",
    0x219AA0AF: "CRct",
    0x219ABA4E: "MC0_RD_BUFFER_CNTL_1",
    0x219C34BD: "tagXUSER_TITLE_PLAYED",
    0x21A3F17B: "XUITimeline",
    0x21A8AF27: "_XMSG_PROPERTY_STRING",
    0x21ABF8A0: "_XSIGNATURE_MEDIA_LICENSE",
    0x21AD1E51: "cMaterial::SOLIDPRI_TYPE",
    0x21B00D8B: "MEMALLOCSTATE",
    0x21B228E3: "_XENABLEGUESTSIGNIN_PARAMS",
    0x21B23A47: "cEm10ActAtkIndiPunch",  # pc-only
    0x21B9DB92: "rSoundRandom::Header",
    0x21BF3451: "_XCONFIG_ALERTDATA_ENTRIES",
    0x21C15B41: "_HVX_IMAGE_USER_MODE_API",
    0x21C4782D: "_D3DXSHPRTSPLITMESHCLUSTERDATA",
    0x21C7666E: "uOma00f_UroPunch::cActPlBase",  # pc-only
    0x21CBC535: "MtLine",
    0x21CC97AC: "cEm10ActSitWait",  # pc-only
    0x21CDB82A: "PA_CL_UCP_1_Y",
    0x21CF4788: "uOm095b_Cliff::cActFall",  # pc-only
    0x21D2DE88: "GPUPERFEVENT_PA_SU",
    0x21D34904: "_GET_USER_SUBSCRIPTION_DETAILS_REQUEST",
    0x21D3B5A5: "uOmUseItem::cActHaveItem",  # pc-only
    0x21D41804: "CXLiveAsyncTaskInternal::RECEIVERATELIMITDATA",
    0x21D77EC0: "std::_String_const_iterator",
    0x21D7A1D7: "cOmContainerAction_liftDown",  # pc-only
    0x21D93DAB: "_TOKEN_SOURCE",
    0x21DBDE50: "uOmFollow::cActBase",  # pc-only
    0x21DC8364: "uAdhesion::ADHESION_OPTIMIZED_TRIANGLE_INFO",
    0x21E2E984: "VGT_PERFCOUNTER2_LOW",
    0x21E98574: "TP3_PERFCOUNTER1_HI",
    0x21ECF823: "_IMAGE_TLS_DIRECTORY32",
    0x21EEAA98: "MC0_PAD_IF_CNTL_2",
    0x21EFF41C: "tagYUV420Frame_WMV",
    0x21F94B11: "cEm6cActDash",  # pc-only
    0x21F975DD: "CG_INT_MASK_REG",
    0x22000965: "EP_HEADER",
    0x2200B729: "MP4MediaRecord",
    0x220589ED: "rEffectList::EFL_PARAM_LENS_FLARE",
    0x220827C4: "cEm10ActAtkBowgun",  # pc-only
    0x220928B2: "cEm40ActSunnySideUpLoop",  # pc-only
    0x22095B84: "XUIMessageFigureGetCount",
    0x220ED655: "uOm08e3_RuinTrap::cActBase",  # pc-only
    0x2210DA45: "cAIFSM::State",  # pc-only
    0x22121CE2: "uEffectVFR::UnitGenerator",
    0x22131A8B: "CCalAacDecoder",
    0x22135809: "TCF_CHICKEN",
    0x2213F7C5: "cEm10ActAtkPlagaHead",  # pc-only
    0x22142D4C: "_XMFLOAT3X3",
    0x22168DC7: "std::_Unchecked_iterator_tag",
    0x221975BD: "cEm83ActDmgBlowL",  # pc-only
    0x221AA7B9: "rEffectList::EFL_PARTICLE_POLYGON_STRIP",
    0x221FCEF5: "std::ctype",
    0x222223E1: "cEm66ActAtkRaftBiteHit_PL",  # pc-only
    0x22269D65: "WAVEFORMATEXTENSIBLE",
    0x222D1D7D: "XUIMessageGetLineIndex",
    0x222D8257: "cEm44ActWalkBgn",  # pc-only
    0x2234BFF9: "XONLINE_ABCH_GET_CONTACTLIST_GAMERTAGS_QUERY_FLAGS",
    0x2239A4F6: "cEm20ActAtkComboExtLoop",  # pc-only
    0x223CBD0C: "HKL__",
    0x223D8DCD: "XGI_SESSIONSEARCHEX_MSG",
    0x223E5C49: "cEm42CActDeathBeatCancel",  # pc-only
    0x2242C3C7: "MtCollision::SimplexSolver::SimplexClosest",
    0x22496C44: "PA_CL_UCP_3_Y",
    0x224B7EF7: "rEffectList::FILTER_OPTION_FLAG",
    0x224CF53B: "_XGLAYOUT_REGION",
    0x224FB2C9: "princeton_digital::stereo_room_3dl2_t",
    0x22546E70: "cPlAction_pl_act_attack_lariat_uro",  # pc-only
    0x22569ABF: "uEffectEdit::MovePathKeyframe",
    0x2258785B: "cUnit::__vftable",
    0x22614CC8: "AZ1_LOOPBACK_PATTERN1PHS1",
    0x22636D7C: "XG_MCT::_MCTQUANTIZATION_TYPE",
    0x2263EAFB: "DRMSTATE",
    0x2265D2DA: "_XMARKETPLACE_ELEMENT",
    0x2266F89F: "rSoundSourceXMA::XMAWAVEFORMAT",
    0x2267A46F: "cEm10ActAtkPlagaH",  # pc-only
    0x226973EF: "uOm1307_Boat::cActMove",  # pc-only
    0x226AE091: "_KUSER_MODE_PTE_BLOCK",
    0x226BFB24: "uBefPlayer",  # pc-only
    0x226C829E: "rSoundDirectionalCurveXml::Element::MyDTI",
    0x226C8A28: "TCF_PERFCOUNTER10_SELECT",
    0x226E9C79: "_XSIGNATURE_ACQUIRE_MEDIA_LICENSES_RESPONSE",
    0x2270E6CF: "sShader::FUNC_SHADOW_CASTER",
    0x227523F6: "ID3DXPatchMesh",
    0x227A8A8A: "cEm82AtkDrillRelease_PL",  # pc-only
    0x227EF643: "PA_SC_DEBUG_CNTL",
    0x2282360D: "rJointEx",  # pc-only
    0x22872B34: "tagWMAFileHeader",
    0x2288B4E5: "XNQOS",
    0x229044F3: "cFSMOrder::FuncParamActBtnHide",  # pc-only
    0x229723DF: "PCIE_PERF_COUNT1_SLV_R_CLK",
    0x229C68F0: "GPUROUNDMODE",
    0x229E73EA: "rAIFSM::ParamBitFlag32",  # pc-only
    0x22A93AD9: "rCameraListXml::MyDTI",
    0x22A94847: "_XSHOWMARKETPLACEUI_ENTRYPOINTS",
    0x22ADCE4A: "SQ_INSTRUCTION_VFETCH_0",
    0x22AE20CD: "XConfigIPTVSettings",
    0x22AFC4D6: "uOmAreaPlHit::cActWait",  # pc-only
    0x22B06DE7: "uEffectEdit::Generator",
    0x22B2821D: "_MESSAGE_RESOURCE_ENTRY",
    0x22B57050: "tagWMAFileStateInternal",
    0x22B7C802: "_ABCH_GET_CONTACTLIST_ITEM",
    0x22BC9951: "cOmCoopBoxAction_pl_act_push_begin",  # pc-only
    0x22BD36F5: "sResource::DecompressStream",
    0x22BE7EE5: "rCameraList::CAMERA_INFO",
    0x22BEC47F: "_stat64i32",
    0x22BEF383: "NetworkMediator",
    0x22C0AE3B: "DO_TEST_DEBUG_TRIGGER_STAT",
    0x22C49B21: "FRAME_BACKCHAIN",
    0x22C51C19: "PCIE_LC_STATE4",
    0x22C6ED9C: "_XMSG_PROPERTY_INTERNAL",
    0x22CCF9B5: "MSI_MSG_ADDR_HI",
    0x22CF7A0E: "sCollision::MyDTI",
    0x22D0EF61: "GPUVSEXPORTMODE",
    0x22D5207A: "NetworkSessionManager::__vftable",
    0x22E3A820: "rEffectList::EFL_HEADER",
    0x22E84A25: "cEmc0ActPreAttack",  # pc-only
    0x22EC09EB: "cEm10ActJump",  # pc-only
    0x22ED0396: "cEm40ActDead",  # pc-only
    0x22FA6C75: "_XEX_SECTION_HEADER",
    0x22FC8E24: "uColorFogFilter::FOG_TYPE",
    0x230041A1: "CCalAudioMetadata",
    0x2305BD06: "XTILETYPE",
    0x23063EF9: "XUIMessageItemHandle",
    0x2306F02A: "RTS_J_W_DY",
    0x23088C77: "XAMINSTRUMENTATION_FORMAT_EX",
    0x2308F7F7: "BufScaleDelay",
    0x230C1F44: "XUISubtimeline",
    0x230D7C0A: "_STFC_PERFORMANCE_PARAMETERS",
    0x2312D95A: "cUnit::TRANS_VIEW",
    0x23185CF9: "CP2_INT_VECTOR",
    0x232417F1: "PCIE_FC_NP",
    0x2324403B: "_XGPOINT3D",
    0x2327E4C8: "_DM_FILEEVENT_DATA",
    0x2328ABD1: "ID3DXMesh",
    0x232DFF6F: "rEffectList::EFL_PARTICLE_ADHESION",
    0x2330979A: "uMultiRadialBlurFilter",
    0x2331E2BF: "_FB_AGGREGATE_REVIEW",
    0x233302FD: "uChain",
    0x23366A39: "XAUDIOMASTERINGVOICEINIT",
    0x23370EC2: "PatInterface::ChatNtc",
    0x233897E4: "_XCREATECONTENTPARAM",
    0x233ABC8E: "cFSMOrderDead::FuncParamDeadSet",  # pc-only
    0x233B1C5D: "cOmContainerAction_wait",  # pc-only
    0x233C9999: "XAUDIODRVPERFCOUNTER",
    0x233F8065: "VGT_DEBUG_REG9",
    0x23425F6B: "cEm41ActTurn",  # pc-only
    0x2345EA14: "CXuiSlider",
    0x234660AD: "sCollision::cColTree::cElemArray",
    0x2348D146: "cEm43ActFootSand",  # pc-only
    0x2349D16F: "_XGAMEINFO",
    0x234E6D26: "_div_t",
    0x234F53C9: "cItAction",  # pc-only
    0x234F9EFC: "cOmBreakAction_wait",  # pc-only
    0x2351A6E6: "COHER_DEST_BASE_7",
    0x23562D3A: "VGT_DMA_SIZE",
    0x2358D582: "cEm40EventAct",  # pc-only
    0x235E9459: "_FP_IEEE_RECORD",
    0x236DAE8B: "XDVO_DEBUG0",
    0x2371A49C: "_DVD_XGD2_DISC_AUTH_RESULT_INVALID_LBA_STATE",
    0x237AD90F: "cEm63Action",  # pc-only
    0x23817EF5: "sBioSound",  # pc-only
    0x23866FF1: "_DXVA_VideoLighting",
    0x238AB4A2: "cEm6fActDie",  # pc-only
    0x238AC5AD: "cNetEm20",  # pc-only
    0x238B0673: "PA_CL_UCP_2_Y",
    0x238B170A: "AdjustDecRange_MT_Ctl",
    0x238B9150: "_XMUICON4",
    0x238F4CE5: "sSoundN::SeVoice",
    0x238F5EB0: "rSoundStreamRequest::SOUND_STREAM_REQUEST_CATEGORY",
    0x239759B6: "VC_DEBUG_REG6",
    0x239803ED: "FSB_TR_DEBUG_HI_AND",
    0x23992185: "_PERSONALIZATION_PARAMS",
    0x239C885A: "uOm1307_Boat::cActWait_E",  # pc-only
    0x239DE4BB: "_XCONTENT_METADATA_TITLE_CONTENT",
    0x23A56055: "cFSMOrderPlayer::FuncParamWeaponTrans",  # pc-only
    0x23A61E0B: "UpsampleRefFrameCtl",
    0x23A6EBB2: "cOmCoopDoorAction_sub",  # pc-only
    0x23A73AF7: "cEm42ActDeadLock",  # pc-only
    0x23ACF968: "cAIAStar",  # pc-only
    0x23ADE948: "rEffectList::EFL_MOVE_PATH_LINE",
    0x23AE352D: "_FILE_NETWORK_OPEN_INFORMATION",
    0x23B37998: "cEm82DmgPinionEnd_PL",  # pc-only
    0x23B729C2: "CP_RT12_POLL_ADDRESS",
    0x23BB8411: "cEm20ActDmgAcid",  # pc-only
    0x23BB8CB5: "EP_NB_MMR_BAR",
    0x23C6A091: "XUISubtimelineProp",
    0x23C9047C: "RecordRangeError",
    0x23CAA73C: "uOm0927_Crane::cActWaitInit",  # pc-only
    0x23CB64A9: "AZ1_PRIMARY_STATE_DWORD2",
    0x23CBFB86: "uOmKickSwitch::cActWait",  # pc-only
    0x23CD7874: "rSoundDirectionalSetXml::Curve",
    0x23CEC5FA: "DMIF_DEBUG01",
    0x23D01052: "__VECTOR_PACK_TYPES",
    0x23D52DDC: "GpuDetile",
    0x23D64A51: "_D3DXCONSTANT_DESC",
    0x23D6ED91: "MtVirtualAllocator::HEAP_INFO",
    0x23D73C52: "rSoundPackage::SoundSource",
    0x23DF73D9: "uOm0892_Lift::cActBase",  # pc-only
    0x23E4DECF: "uOmSwitch3::cActLoopBase",  # pc-only
    0x23E5502F: "_Q_MESSAGE_SUMMARY_MSG",
    0x23F13DF5: "_s__RTTIBaseClassArray",
    0x23F44C3E: "MH_STATUS",
    0x23F63BFF: "rSoundRandomXml::ElementData::MyDTI",
    0x23FA1DA3: "_XPRIVILEGE_TYPE",
    0x23FA4545: "CXuiBase",
    0x23FB46A2: "_tagDRM_ID",
    0x23FC9D38: "cOmRollAction_break",  # pc-only
    0x24006A92: "XDVO_DEBUG4",
    0x24046806: "MtCollisionTree::RadixSortMT::__vftable",
    0x2409BA4F: "std::locale::_Locimp",
    0x240A9178: "uShadow::PCF_FILTER",
    0x2415E5E8: "cEmc0ActWait",  # pc-only
    0x24195A71: "cEm0cActAttack",  # pc-only
    0x241C8F35: "MP4MPEGSampleEntryAtom",
    0x241D27AD: "TPC_CHICKEN",
    0x241D2A9C: "uEffectEdit::LifeKeyframe",
    0x241DED94: "TCD_STALLS_DEBUG",
    0x241F5DEB: "rTexture",
    0x2423D671: "RTS_WD_EDGE_0_DIST_LSBS",
    0x24274D7B: "GPUFLOW_INSTRUCTION_PAIR",
    0x24293112: "_KMUTANT",
    0x243927D2: "uEffectEdit::LINE_FIX_WORK",
    0x24394564: "MC1_PERFCOUNTER0_CNTL",
    0x243AFC19: "_P_QUERY_AFFILIATES_REPLY_DATA_MSG",
    0x243BAAB8: "BSB_WRAPPER_PRBS_CTRL",
    0x243C2ED6: "rEffectList::PATH_OPTION_FLAG",
    0x243C62FF: "COHER_DEST_BASE_3",
    0x243C7E83: "CCalImagePlayer::AnimationDirection",
    0x243D33AA: "uOmArea::cActBase",  # pc-only
    0x243D7758: "VOICECHAT_EXTENSION",
    0x243EA3F3: "sEffect::MyDTI",
    0x243EAA7B: "rEffectList::CULLING_OPTION_FLAG",
    0x2440302E: "uCamera::MyDTI",
    0x24410398: "MC1_INTERRUPT_STATUS",
    0x2444B7F8: "MSI_CAP_LIST",
    0x2444DE7F: "D1MODE_PRIORITY_A_CNT",
    0x24470BC6: "rEffectSetData::CHAIN_BLEND_TYPE",
    0x2447D742: "sId::rIdMapList",  # pc-only
    0x244846D6: "GPUBLENDOP",
    0x244CA173: "CCalFileStream::__vftable",
    0x244F1605: "cEm65ActWalk",  # pc-only
    0x245036B2: "cFSMOrderEm10::FuncParamAttr_Em10",  # pc-only
    0x2452670E: "FSB_LX_DEBUG_HI_OR",
    0x24543796: "IOC_BSB_MST_CPL_CRC_0",
    0x24591A61: "MP4SampleDescriptionAtom",
    0x245ACE41: "ID3DXMatrixStack::__vftable",
    0x245FC51E: "cEm44ActThreat",  # pc-only
    0x24619C67: "aS200::cActEvBoatAirRideOff",  # pc-only
    0x24642B22: "IXAudioRenderEffect::__vftable",
    0x24673FB7: "MH_PERFMON_PERFCOUNTER2_LOW",
    0x24688A11: "_P_FIND_USER_MSG",
    0x24691375: "NetworkUnit",
    0x246A2E96: "cEm10ActAtkGunShot",  # pc-only
    0x246BA7C1: "uAdhesion::ADHESION_TRIANGLE_NODE",
    0x246D0E06: "DC_SURFACE_0_INFO",
    0x246F86DB: "_D3DXPASS_DESC",
    0x246FAF8B: "AZ0_MRU_BANK7_DEPTH_MASK",
    0x24732ECE: "DCP_CRC_MASK",
    0x24737B4C: "_XUSER_FRIENDS_LIST_INFO",
    0x2473EE76: "_TITLE_DETAILS_RESPONSE",
    0x24751E68: "cPlAction_pl_act_item_get_second",  # pc-only
    0x247765DE: "_ChexTileInfo",
    0x2477BDEB: "PCIE_CORR_ERR_STATUS",
    0x247A92D4: "D3D::Edram",
    0x247DE067: "_COPP_TVProtectionStandard",
    0x247EEB9B: "rArchive::DecompressStream",
    0x247FA510: "sPrim::Prim::FRESNEL_DATA",
    0x2482BBE2: "sLightLinker::EffWind",  # pc-only
    0x248359E9: "tagCInputBitStream_WMV",
    0x2483F3FD: "RB_MODECONTROL",
    0x248E967F: "tagWMVAsyncDecodeState",
    0x248FBF27: "_PM4CMDLOADCONSTANTCONTEXT",
    0x2490846B: "uBioActorPL01Face",  # pc-only
    0x2491A5A0: "MtInterlock",
    0x249367FE: "cEm10ActDmgAppearPlaga",  # pc-only
    0x24961702: "GPUCMPFUNC",
    0x24967063: "COHER_SIZE_PM4",
    0x249D00B2: "rEffectSetDataList::ESL_HEADER",
    0x249D103D: "sCollision::Sbc::MyDTI",
    0x24A301E3: "DMIF_DEBUG05",
    0x24A67EF7: "_D3DPWLGAMMAENTRY",
    0x24ACE27E: "cEm10ActPara_L",  # pc-only
    0x24AF16C7: "uOmSwitch::cActMessage",  # pc-only
    0x24B298DF: "uLightShaft::MyDTI",
    0x24B30FCE: "_DUMP_COLLECTION_HELP",
    0x24B80E7B: "_XPRESENCE_SEND_ALIVE",
    0x24BA1634: "_output_l::__l83::_count_string",
    0x24BB5500: "rEffectList::RANGE_DIR_TYPE",
    0x24BCE4BF: "uCubeMapLight",
    0x24BE7775: "sPrim::PIPELINE_PRIM",
    0x24C46A60: "cEm82KnifeEvent",  # pc-only
    0x24C67D9D: "PARSESTATE",
    0x24CC5A4D: "FSB_LR_CTRL_OR",
    0x24CC7F65: "_IMAGE_DEBUG_DIRECTORY",
    0x24D2CC75: "uOm1303_Truck::cActBase",  # pc-only
    0x24D32BA8: "MP4TrackFragmentAtom",
    0x24D6F484: "cEm32ActTongueCatch",  # pc-only
    0x24DC2B0A: "cAIFSM::ParamSubCondition",  # pc-only
    0x24E01F00: "uOma005_Stairs::cActWait",  # pc-only
    0x24E1AA9D: "_XPROFILE_RACE_CAMERA_LOCATION_OPTIONS",
    0x24E2FA51: "sResource::RemoteInfo::MyDTI",
    0x24E584F3: "cEm41ActNearCatchOk",  # pc-only
    0x24E9D2EE: "_TOKEN_PRIVILEGES",
    0x24EB3CB9: "XUIMessageChecked",
    0x24F03F61: "_LDBL12",
    0x24F3637F: "TP0_PERFCOUNTER0_LOW",
    0x24F59FF5: "GPUADDRESSCLAMP",
    0x24F8732D: "PA_SU_PERFCOUNTER1_LOW",
    0x24F88EFF: "_MIGRATE_XBOX1_USER_RESPONSE",
    0x24F8E0FC: "cEm44Action",  # pc-only
    0x24F8EB8A: "sSoundN::ExternalVoice",
    0x24FA9DAF: "VC_DEBUG_REG2",
    0x2504A7C6: "uOmJeep::cActWepDmgFire",  # pc-only
    0x2507561B: "cOmCoopBoxAction_sub",  # pc-only
    0x2507FA05: "MtFloat4x4",
    0x2507FA42: "cEm0bActTurn",  # pc-only
    0x2509D8C0: "cBioLog",  # pc-only
    0x2509F2E3: "FSB_LX_LERST_XSTP",
    0x250ABD29: "uOm0927_Crane::cActWaitBase",  # pc-only
    0x2515F3D3: "cTrans::PASS",
    0x251B5A69: "cEm84ActDownStrippedEnd",  # pc-only
    0x251E4CC1: "sPad::PAD_VIB",
    0x25239088: "SB_REVISION_ID",
    0x25251A08: "PCIE_RX_CREDITS_ALLOCATED_CPLD",
    0x2525AE65: "ROM_PORT_REG",
    0x2527A442: "XUSER_ACHIEVEMENT",
    0x252E5F65: "PatInterface::LayerUserPosition",
    0x2530F45C: "RTS_EDGE_DIST_MSBS",
    0x25312ABC: "XG_MCT::CSimpleEntropyDecoder",
    0x2533673C: "PCIE_RX_DLLP0",
    0x253B219B: "PatInterface::Kick",
    0x253BE8A4: "_XMUDHENN3",
    0x253FCA51: "XONLINE_BASIC_CONTENT_INFO_FLAGS",
    0x253FEC50: "_GET_POSTAL_CODE_REQUEST",
    0x254450A4: "CP_RT_BIN_SELECT_LO",
    0x254AA148: "_D3DVOLUME_DESC",
    0x254B9FD8: "uOmClutch::cActPlClutched",  # pc-only
    0x254E37B6: "cEm4501ActWait",  # pc-only
    0x254EAB32: "_PIX_NOTIFICATION",
    0x254F5732: "CONTENTENCRYPTIONOBJEXT",
    0x254F5A32: "_XHTTP_REQUEST",
    0x2551C734: "uEffectEdit::Culling",
    0x255B124A: "CXLivePlayerList",
    0x255BA88F: "_XMSTV_CREATE_CERTIFICATE_REQUEST",
    0x255FB697: "TP_PERFCOUNT_SELECT",
    0x255FD7AE: "uOmClutch::cActPlBase",  # pc-only
    0x2562DBD8: "uOmS508_Break::cActPlBase",  # pc-only
    0x2569B14D: "rCollision::MyDTI",
    0x25714005: "uModelEdge",
    0x257163FE: "uOmS204CrouchPoint::cActBase",  # pc-only
    0x25723D04: "_DVD_XGD2_DISC_AUTH_RESULT_CHALLENGE",
    0x257929B3: "rSoundSource::WAVEFORMATEX",
    0x257F1ABA: "cEm10ActTurn",  # pc-only
    0x25804656: "MOVE_LINE",
    0x258162AE: "CAacDecoderChannelInfo",
    0x25828C68: "AZ1_LOOPBACK_RX_CRC_MASK",
    0x258393A6: "_XMXDEC4",
    0x2585F3C0: "cAIFSM::ParamProperty",  # pc-only
    0x25890A33: "cFSMOrder::FuncParamMessageSce",  # pc-only
    0x258EF796: "_WHOLESALE_INFO",
    0x259025DB: "D1SCL_COEF_RAM_SELECT",
    0x25928284: "RTS_I_W_DY",
    0x2593A3E8: "XNetConfigSectorHeader",
    0x25985D33: "cEm82AtkDrillWait_PL",  # pc-only
    0x25998008: "rSoundSourceMusicInterMediate::MyDTI",
    0x259AA0F4: "_DXVA_DeinterlaceQueryAvailableModes",
    0x259DBEDE: "XECRYPT_SHA512_STATE",
    0x259EF565: "SQ_INSTRUCTION_CF_LOOP_2",
    0x259F5293: "_XONLINE_STATS_ENUM_BY_RATING_REQUEST",
    0x25A25859: "_D3DHIZENABLEMODE",
    0x25A6CEB4: "_strflt",
    0x25A8D800: "PCIE_LC_STATE0",
    0x25A917FE: "sCamera::VIEWPORT_NO",
    0x25A9E3D9: "_FP_128",
    0x25ABB6A6: "rEffectStrip::INDEX_PARAM",
    0x25ABBDB9: "CXContentDownloadMedia",
    0x25B1157A: "_ImageArchitectureEntry",
    0x25BC0CB2: "sRender::TempTexture::MyDTI",
    0x25C3B496: "FSB_TX_PMCTRL",
    0x25C50D3A: "cFSMOrder::FuncParamActBtn",  # pc-only
    0x25C661A2: "D1CRTC_DOUBLE_BUFFER_CONTROL",
    0x25C9A737: "cPlAction_pl_act_attack_add",  # pc-only
    0x25C9C830: "_IMAGE_IMPORT_BY_NAME",
    0x25CB4C8F: "GPUCmdFrameBegin",
    0x25D73B1B: "MtFile::MyDTI",
    0x25DAE3F5: "UVCHANNELSTATUS",
    0x25E3A425: "_XUISTRINGTABLE",
    0x25ED42DB: "rBioTree",  # pc-only
    0x25EF8DD8: "sCollision::PreTraverseInfo::PreTraverseData",
    0x25FCF81B: "FSB_TX_PMC3_AND",
    0x26009ED2: "PCIE_CFG_SCRATCH0",
    0x2600B64A: "cPlAction_pl_act_item_use_my_second",  # pc-only
    0x2609D2D4: "_PixSmallOpcodesType",
    0x260EC12E: "FSB_LX_IDLE_PATT_AND",
    0x261132D1: "TCA_PROBE_DEBUG",
    0x26170322: "cFSMOrderPawn::FuncParamEventAct",  # pc-only
    0x2617997D: "sCollision::HIT_MODE",
    0x2618202E: "MtCollisionGjk::ClosestPointInfo",
    0x2618B724: "cPositionEvaluationVisibilityToPos",  # pc-only
    0x261B1BBF: "cOmCoopGateAction_om_act_opening",  # pc-only
    0x261D6B6B: "ID3DXSaveUserData",
    0x261E07B6: "std::_Allocator_base",
    0x261FFCF7: "_XASYNCMESSAGE",
    0x262674AB: "CP_DMA_SRC_ADDR_STAT",
    0x2629F93A: "GPUFrameInfo",
    0x262ADC0E: "sTool",
    0x262DC874: "CP_RT10_MASK",
    0x26385D2E: "cEm30ActWalk",  # pc-only
    0x2638D12F: "NetworkUnitPacketPool",
    0x263D50D8: "CFG_MMR_BAR",
    0x2642691E: "_DRM_AES_ENCRYPT_OPTION",
    0x26426DAA: "RB_COPY_CONTROL",
    0x26454214: "ISDEPENDENCYREC",
    0x26468573: "cEm8eAtkDrillAct",  # pc-only
    0x264C857F: "cEm44ActBack",  # pc-only
    0x264F4E37: "TP2_PERFCOUNTER1_HI",
    0x264F943C: "cEm30ActSnarl",  # pc-only
    0x265229D0: "NetworkRanking::__vftable",
    0x2655CAA0: "rNavigationMeshDae::Cluster",  # pc-only
    0x2658334A: "EP_REGPROG_INF",
    0x265D06E1: "cPlAction_pl_act_damage_flash",  # pc-only
    0x265E3B96: "FSB_LX_ERRINJ0_AND",
    0x265F741E: "_IMAGE_FUNCTION_ENTRY",
    0x265FB213: "_FB_PLAYER_REVIEW_REQUEST",
    0x26602BF5: "rSoundStreamRequest::Element",
    0x26688973: "_LDRX_PLUGIN",
    0x266DB579: "PCIE_RX_CREDITS_RECEIVED_D",
    0x266E8A91: "rLinkUnit",  # pc-only
    0x267350D1: "TCF_PERFCOUNTER4_LOW",
    0x2675F5C9: "tagCodeBookDescription",
    0x267BDE14: "MtThread::STATUS",
    0x267C40EE: "BIOS_12_SCRATCH",
    0x267EE511: "XAUDIO::CXMASourceEffect::CResamplerBatch",
    0x267F83DB: "CXHttpDownloadToCache",
    0x26812A68: "NetworkCommunityLive::moveGetAccountSelfLanguage::__l3",
    0x26814A2E: "cPlAction_pl_act_damage_guard",  # pc-only
    0x268AD3C6: "GPUCmdDetile",
    0x268C9859: "XAUDIO::CWaveFile",
    0x268D80DA: "rCameraListXml::CameraInfo::MyDTI",
    0x26926C0A: "CP_FUNCTION",
    0x2694CB3A: "cEm45ActPickup",  # pc-only
    0x26990154: "uOmCoopJumpBroad::cActJump",  # pc-only
    0x269F9A82: "CREATE_OWNER_ACCT_RESPONSE",
    0x269FBFCE: "uEffectVFR::GridNorm",
    0x26A0D870: "_FULLPATHHELPER",
    0x26A2F60C: "XAUDIOSOURCEFXPACKETCALLBACK",
    0x26A6396D: "tagWMVRect",
    0x26A9F62D: "cTrans::OffscreenSurface",  # pc-only
    0x26AA1F10: "_COMPOUND_ACCESS_ALLOWED_ACE",
    0x26ACE202: "cEm43ActShakeAttack_Pl",  # pc-only
    0x26AD6076: "D3D::Queue_Commands",
    0x26AD9E6C: "_SCOPE_TABLE",
    0x26ADE507: "XAUDIO::CRouterEffect",
    0x26AE7963: "rCloth::Chain",
    0x26B25A80: "FSB_TX_CMDMM1_AND",
    0x26B30C94: "SurfaceFormat",
    0x26B3D8E3: "cEm0cActMove",  # pc-only
    0x26B5C952: "uEfCam",  # pc-only
    0x26B72EBD: "_XMSHORT4",
    0x26B943AA: "_MEMORYSTATUS",
    0x26BA3764: "cEm22ActDmgActBtn",  # pc-only
    0x26BC649B: "PatInterface::InviteId",
    0x26BC8AB3: "cHitTree",  # pc-only
    0x26BE9005: "MP4MPEGMediaHeaderAtom",
    0x26C410F6: "PA_CL_UCP_5_Y",
    0x26CB5771: "cEm10ActAtkChain",  # pc-only
    0x26CC4E9A: "CFFOLDER_HMAC",
    0x26D93006: "_XUSER_PROPERTY",
    0x26D9D292: "FSB_TLA_PATTERN0",
    0x26DE31C8: "_XPROFILE_SETTING_SYNC_RESULT",
    0x26E0EA9C: "cEm83ActEquip",  # pc-only
    0x26E3A03B: "RBBM_CNTL",
    0x26E57F79: "cEm83PlEvent",  # pc-only
    0x26EC7815: "uDOFFilter::DOF_TYPE",
    0x26EDFAEC: "MtPreProcessor::DefaultInclude::MyDTI",
    0x26F00F1C: "XUIMessageChar",
    0x26F2CA5C: "uOmS104_Driver::cActDead",  # pc-only
    0x26F3E895: "CXHttpDownloadBase::__vftable",
    0x26F84990: "sId::Id",  # pc-only
    0x26F86FEB: "uUniformShadow",
    0x26F88E79: "TCF_PERFCOUNTER10_HI",
    0x26F8A758: "_XREFERRAL_LOCATION",
    0x26FA6CFC: "IXHVExternalCodec",
    0x2704AB5E: "XMARKETPLACE_OFFERING_TYPE",
    0x27067AC1: "PA_CL_UCP_4_Y",
    0x27085191: "cEm45ActTurn",  # pc-only
    0x2711C215: "SCHEMA_HEADER",
    0x2711CB87: "_XER",
    0x27142820: "cNetEm41Core",  # pc-only
    0x271463AF: "_IMAGE_FILE_HEADER",
    0x27170DF2: "XAUDIO::CMasteringVoice",
    0x2719C951: "uSoundEngine",  # pc-only
    0x271D560C: "RB_COPY_SURFACE_SLICE",
    0x271EEF32: "cEm20ActDmgSpin",  # pc-only
    0x271F9533: "XGI_SESSIONSEARCHBYID_MSG",
    0x271F9990: "cEm20ActAtkHangingTate",  # pc-only
    0x27219157: "CP_BIN_SELECT_LO",
    0x2724ADD2: "HZ_PERFCOUNTER0_SELECT",
    0x272532B5: "SB_LATENCY",
    0x272B0A92: "_DM_SET_INPUT_STATE",
    0x272D07D0: "_UTILITYPROCPARAMS",
    0x2732D65E: "NetworkSessionManagerBroadcast",
    0x27333E5C: "SETUP_DEBUG_REG2",
    0x27376A2B: "_XBOX_HARDWARE_INFO",
    0x27394CF3: "CAudioObjectDecoder",
    0x273A8522: "_PRESENCE_SET_GAME_SESSION",
    0x274AC7B8: "_GET_ACCOUNT_INFO_RESPONSE",
    0x274D197D: "TCO_QUAD0_DEBUG0",
    0x27529FB8: "cEm10ActAtkGunWarnShot",  # pc-only
    0x2752DB8D: "PCIEP_SCRATCH",
    0x275A6B6C: "NetworkCommunityLive::moveGetUserBinary::__l3",
    0x275B3BC9: "_XMFLOAT4X3",
    0x275BD863: "XUINamedframeData",
    0x275C1AD5: "cEm10ActDmgLeg",  # pc-only
    0x2762254C: "uBioActorPL00Simple",  # pc-only
    0x276259F0: "cPlAction_pl_act_jump_broad_4m",  # pc-only
    0x276994F4: "AZ0_MRU_BANK3_DEPTH_MASK",
    0x276DE8B7: "rEffect2D",
    0x277036A7: "_SHARE_ACCESS",
    0x27711B61: "uOm095b_Cliff::cActWait",  # pc-only
    0x2771DC19: "CXFriendsRequest",
    0x2779EC82: "cEm22ActDieLie",  # pc-only
    0x277A52B8: "_P_PEER_PRESENCE_ITEM",
    0x277A5D5B: "tagRecoverFixUp",
    0x277E93B9: "sPrim::Prim::OCCLUSION_DATA",
    0x27853DCA: "BSB_WRAPPER_PHY90_BACKUP",
    0x27857518: "LINK_STATUS",
    0x27860B38: "AAC_DECODER_INSTANCE",
    0x27862B36: "cEm8cAtkGroundHitEnd",  # pc-only
    0x2786433C: "CXuiList",
    0x278CAE59: "rSoundPackage::MyDTI",
    0x2796CF65: "MC1_TIMING_CNTL_2",
    0x279750B5: "BSB_INT_VECTOR",
    0x2799C649: "cTrans::CMD_PROFILE",
    0x279F10D6: "DEVICE_CAP",
    0x279F4574: "cItAction_it_act_put",  # pc-only
    0x27A1B24A: "cEm10ActAtkGunEmpShot",  # pc-only
    0x27A785D3: "cEm41ActMissileRegene",  # pc-only
    0x27A7F292: "cEm8cAtkArmAttack",  # pc-only
    0x27AED7E2: "uOmWallStick::cActWallStick",  # pc-only
    0x27B4D200: "cEm43ActRageStart",  # pc-only
    0x27BC956F: "_USER_ACCOUNT_STATUS_INFO",
    0x27C05216: "rEffectSetData::ESD_SET_RADIAL_BLUR_FILTER",
    0x27C6F212: "IDirectXFileEnumObject",
    0x27CE3B23: "CCalGraphicsRenderer",
    0x27D1288A: "_VD_WSS_DATA",
    0x27D40351: "GC_PMI_NXT_CAP_PTR",
    0x27D9AEB6: "cAnimRect::Key",  # pc-only
    0x27DB6FD7: "MtXmlReader::__vftable",
    0x27DD3FD2: "cFSMOrder::FuncParamEventTask",  # pc-only
    0x27E941DC: "rSoundSeGenerator::BigBoxInfo",  # pc-only
    0x27E99E48: "GC_COMMAND",
    0x27EAE89D: "rCollada",
    0x27EC33D1: "tagWMAFileHdrState",
    0x27EEC3E7: "cSystem",
    0x27F0883B: "CommonEffectParam",  # pc-only
    0x27F4BF1A: "cEm41ActRegeneFull",  # pc-only
    0x27F629A7: "_P_IS_AFFILIATE_MSG",
    0x27F66316: "cAIPathCostManager::CostInfoCounter",  # pc-only
    0x28068F0F: "D1CRTC_OVERSCAN_BOTTOM",
    0x280B5A7B: "CP_RT_ST_BUFSZ",
    0x28155CDC: "cEm61ActDmgAir",  # pc-only
    0x28165D80: "CP_RT13_SIZE",
    0x2819D205: "rAHEffectXml",  # pc-only
    0x2819E802: "DCP_CRC_P0_CURRENT",
    0x281AE264: "sCollision::cColArray",
    0x281C3DC2: "cOmRider2ActWait",  # pc-only
    0x28200B63: "XCOMPRESS::decision_node",
    0x282ADC45: "NetworkStorage::Results",
    0x282B3BEB: "sShader::__vftable",
    0x282F44D8: "cPlAction_pl_act_wall_stick_t_ready_fail",  # pc-only
    0x283226C2: "PCIE_RESERVED",
    0x28357BAD: "RB_PERFCOUNTER2_LOW",
    0x283B44CB: "HFRegenStruct",
    0x284B3095: "CP_RT_BIN_SELECT_HI",
    0x28506A5F: "SCLK_PWRMGT_CNTL3_REG",
    0x28542670: "cFSMOrder::FuncParamTimer",  # pc-only
    0x285614B9: "uOmKickSwitch::cActPlKick",  # pc-only
    0x28562EEE: "CP_D2_EOL_SOF_COUNTER",
    0x285835D4: "MtDTI::ATTR",
    0x285B7CDF: "MP4SyncSampleAtom",
    0x285C7A5F: "rEffectList::PATH_RELEASE_TYPE",
    0x285DA48E: "ID3DXBaseEffect::__vftable",
    0x28615355: "DVOACLK_CNTL",
    0x28666198: "cEm10ActDmgArmWeapon",  # pc-only
    0x286A789A: "cEm80PlEvent",  # pc-only
    0x286E717A: "D3D::CCapture::__vftable",
    0x2870BAD0: "uToneMapFilter::StarDef",
    0x2871B8E3: "_XMSHORTN2",
    0x2871E172: "uEffectVFR::PTCL_STATUS",
    0x28735025: "FSB_LR_DEBUG_HI_AND",
    0x28758CED: "CRTC1_DEBUG_03",
    0x2879DF0F: "rEffectSetData::ESD_MOVE_PATH_STRIP_COLL",
    0x287A1771: "cEmc2ActRelease",  # pc-only
    0x287AB61D: "sTransition",  # pc-only
    0x287EBE16: "_IMAGE_IA64_RUNTIME_FUNCTION_ENTRY",
    0x28810F1D: "cEm20ActAtkExecKill",  # pc-only
    0x288419E0: "XnQosLookupInfo",
    0x2885D407: "WmaGetDataParam",
    0x2889B906: "sPrim::FUNC_PRIM_EX",
    0x288F7E74: "uJointAnimator",
    0x288F8417: "cPlAction_pl_act_attack_finish",  # pc-only
    0x28917468: "MtAutoCriticalSection",
    0x289375F5: "CHAINACTIONTAG",
    0x289718A7: "_XMSG_FLAGS_REQUEST",
    0x2899D329: "tRect_WMC",
    0x289CE1D9: "SCL1_VFILT_COEF",
    0x289D310E: "STRMDECMSGMSGINFO_DECODE",
    0x289EF050: "std::fpos",
    0x28A37435: "rModel::PRIMITIVE_INFO",
    0x28A5B877: "_TEAM_ENUM_BY_XUID_RESULTS",
    0x28A5CF91: "_EEDID",
    0x28A74CCB: "_D3DXFUNCTION_DESC",
    0x28A831ED: "sEffectBase",
    0x28B1A428: "cEm30ActDieInstant",  # pc-only
    0x28B1C5B8: "cEm10ActDeadNormal2",  # pc-only
    0x28B1FE7B: "cFSMOrderItem::FuncParamItemCheck",  # pc-only
    0x28B3E62E: "cEm30ActWalkFast",  # pc-only
    0x28B59481: "cEm42TActMotOnce",  # pc-only
    0x28B7873B: "XAUDIO::CBatchAllocatedObject",
    0x28BF1343: "GpuFrameType",
    0x28C4F6A6: "FSB_LR_DEBUG_AUX_AND",
    0x28C5F250: "FSB_TX_TFIRST",
    0x28CD8EEB: "uCameraLight",  # pc-only
    0x28CE3195: "D3D::SwapData",
    0x28D5E2D9: "rSoundCurveXml::Element::MyDTI",
    0x28D93330: "IDirectXFileDataReferenceVtbl",
    0x28DB9138: "_P_REPLY_BUDDY",
    0x28E09794: "D3D::CRingAllocList",
    0x28E25F3E: "uIdSaving00",  # pc-only
    0x28E28724: "AZ1_MRU_BANK6_DEPTH_MASK",
    0x28EB7C61: "XGI_WRITESETTINGS_MSG",
    0x28EC8E84: "rTexture::MyDTI",
    0x28F54A13: "uEffectVFR::MovePathChain",
    0x290393D7: "XNKEY",
    0x29051A35: "_D3DRECT",
    0x290574EC: "SQ_VS_CONST",
    0x2908475A: "EFC_PARAM_F32_RANGE",
    0x29090DB5: "rEffectList::EFL_PARTICLE_POLYLINE",
    0x290C294C: "FSB_TX_PMC2",
    0x290EDE5D: "_D3DGPUVERSION",
    0x291136A0: "PCIE_PERF_COUNT1_MST_C_CLK",
    0x291BAA11: "MC1_RD_STR_DLY_1",
    0x291CFAF6: "VIDEOFORMAT",
    0x291D0803: "cEm66ActSwim",  # pc-only
    0x291D1C28: "sRender::RENDERMODE_FLAGS",
    0x2921D62B: "_XSHOWDEVICESELECTORUI_PARAMS",
    0x29233584: "cEmc1Action",  # pc-only
    0x2924B4CC: "DO_TEST_DEBUG_OUT_PIN_MASK",
    0x2929CEC8: "D3D::RemoveDebugInfoHelper",
    0x292AD6D7: "cEm0cActReadyEnd",  # pc-only
    0x292D0194: "XGI_STATSWRITE_MSG",
    0x292FCA02: "cEm10ActAtkPlagaHeadBack",  # pc-only
    0x29307BC7: "MC0_DLL_MASTER_ADJ_0",
    0x2930802E: "uEffectEdit::LightKeyframe",
    0x2931C971: "std::codecvt",
    0x2933A571: "TCF_PERFCOUNTER2_LOW",
    0x2933FF26: "TCR_PERFCOUNTER0_HI",
    0x29347F35: "sLightLinker::BakeInfo",  # pc-only
    0x29380CBF: "sPhysics::RIGID_BODY_SHAPE",
    0x293EEC37: "uEffectVFR::MoveBase",
    0x293EED24: "NCI_VOICE_PROPERTIES_BLOCK",
    0x29408039: "uOmKickSwitch::cActKicked",  # pc-only
    0x2940F1D5: "aS109::cActJeepContinue",  # pc-only
    0x29411285: "uEffect2D::STATUS",
    0x294115EE: "MH_PERFMON_PERFCOUNTER1_HI",
    0x294367E4: "uOmCrouch::cActWait",  # pc-only
    0x294E8453: "cEm10ActAtkGunAimStartMG",  # pc-only
    0x2953C0AC: "sApp",
    0x2954AA9A: "XONLINE_CONTENT_ENUMERATE_FLAGS",
    0x2954BE44: "cEm10ActAtkBowReload",  # pc-only
    0x2958A792: "AUDIOSTREAMINFO",
    0x295AC026: "_XSTATS_POST_REQUEST",
    0x29616ABE: "MtHeapAllocator::MyDTI",
    0x2961BD66: "PA_SU_DEBUG_DATA",
    0x296640B1: "_HEAP",
    0x2967A5F9: "D1OVL_ENABLE",
    0x2968ECB0: "XECRYPT_RC4_STATE",
    0x296F1CB4: "uModel::Motion::STATE",
    0x296F5EFE: "cAction",  # pc-only
    0x296FB237: "cWpAction_wp0d_act_load_ground_second",  # pc-only
    0x29771292: "_TOKEN_DEFAULT_DACL",
    0x297C394F: "cEm41CActDiscloseDamage",  # pc-only
    0x297DAE79: "_LocaleUpdate",
    0x29873FCA: "_TIME_ZONE_INFORMATION",
    0x2988BF09: "CXStorageDownloadWorker::RESOLVE_NAME_RESPONSE_BUFFER",
    0x298A3CAF: "MC1_DRAM_DATA",
    0x29939638: "_D3DMATERIALCOLORSOURCE",
    0x2994D15B: "_P_ALIVE_REPLY_MSG",
    0x29952805: "_CACHEHASHTABLEENTRY",
    0x29A8FFEE: "cFSMOrder::FuncParamSetFlag",  # pc-only
    0x29ACBFC3: "_FPIEEE_VALUE",
    0x29B1DEAB: "uOmCrank::cActWait",  # pc-only
    0x29B21853: "XAUDIO::XAUDIOVOICEROUTECTX",
    0x29B42C51: "uOmS705ceil::cActStop",  # pc-only
    0x29B5C2E5: "HSIO_DLL_ADJ8",
    0x29BB2C1C: "_auencOutputParams",
    0x29BF9D9C: "tagLC_ID",
    0x29C21E9E: "TCO_QUAD3_DEBUG0",
    0x29C286AF: "cPlAction_pl_act_damage_lie_wait_front",  # pc-only
    0x29C36C68: "SCLK_G_SCL1_CNTL",
    0x29C620AF: "XUINotifyScrollBarChanged",
    0x29C8FBDA: "MC1_ARBITRATION_CNTL",
    0x29CBAAC3: "CCalPlayer::__vftable",
    0x29D05621: "GPUENDIAN128",
    0x29DB4486: "cEmc2ActCatch_Pl",  # pc-only
    0x29E58B35: "D3D::BufferResource",
    0x29E86185: "cNetEm62",  # pc-only
    0x29EC8BCF: "CP_IB1_BUFSZ",
    0x29EEC7CF: "LIST_ENTRY64",
    0x29F21EF6: "uActorModel::EffectEmitter::CONTROL_FLAG",
    0x29F6F4F4: "_CSVChal",
    0x29F928FA: "cEm20ActAtkYoko",  # pc-only
    0x29FA017E: "cNetEm71",  # pc-only
    0x29FBD45B: "cEm0bActAtkCatchHit_PL",  # pc-only
    0x2A01A0EA: "_STFC_DIRECTORY_ENTRY",
    0x2A020D04: "tagCVector",
    0x2A031018: "MtPropertyList",
    0x2A047B25: "XAUDIO::CSourceEffect",
    0x2A04B00F: "MtCollada::LookAt",
    0x2A0597F8: "_XSHOWSIGNINUI_PARAMS",
    0x2A09CE10: "rSoundSource::MyDTI",
    0x2A0B9EAB: "rSoundStreamRequestXml::TargetPlatform",
    0x2A0C9112: "cAIDynamicPathFinding::GroupManagement",  # pc-only
    0x2A0D1371: "NB_ADAPTER_ID_W",
    0x2A0F65BC: "CP_RT9_REFERENCE",
    0x2A106601: "XAUDIO::CRoutedVoice",
    0x2A1100CC: "MtFile::SEEKBASE",
    0x2A11951F: "_QUERY_REMOVE_REQUEST",
    0x2A11C04E: "EFC_KEYFRAME_COLOR",
    0x2A1212A5: "CP_CODE_ID",
    0x2A1391CF: "std::ios_base::failure",
    0x2A18E945: "XECRYPT_SHA384_STATE",
    0x2A1B2F82: "PA_SC_DEBUG_SR_1",
    0x2A1BE5DF: "XAUDIOSOURCEVOICEINIT",
    0x2A1CA77B: "rEffectSetData::COLOR_FLAG",
    0x2A2373B5: "CXLiveLogon",
    0x2A238138: "cOmCoopTwistActFinish",  # pc-only
    0x2A28E8EE: "IClassFactory::__vftable",
    0x2A29ADDB: "cEm42CActWait",  # pc-only
    0x2A2E70C0: "cResource::ATTR",
    0x2A2EF166: "CP_BIN_SELECT_HI",
    0x2A2FDD2F: "XAMINSTRUMENTATION_FORMAT",
    0x2A335C4B: "cPlAction_pl_act_knife_ready_end_to_weapon_ready",  # pc-only
    0x2A3360F6: "_KDRIVER_NOTIFICATION_TYPE",
    0x2A33DEE0: "_D3DHIZFUNC",
    0x2A358D06: "uNavMeshNodePickUp",  # pc-only
    0x2A35DE3A: "cEm32ActStep",  # pc-only
    0x2A3FD283: "_FB_GET_AGG_REVIEWS_REQUEST",
    0x2A3FE647: "cEm30PlEvent",  # pc-only
    0x2A403D3E: "CCalBase::NOTIFICATION_TYPE",
    0x2A409A4F: "GPUPERFEVENT_TCF",
    0x2A42780A: "princeton_digital::occlusion_t",
    0x2A43D68B: "Replicator",
    0x2A4493D4: "_I3DL2_OBSTRUCTIONPROPERTIES",
    0x2A44F566: "cEm42CActEnter",  # pc-only
    0x2A4B1C53: "CCalAudioPlayer",
    0x2A52D000: "cOmBoatAirAction_pl_act_ride_on_ready",  # pc-only
    0x2A5352CB: "PCIE_HDR_LOG2",
    0x2A57AB50: "uOm0912_s119Tram::cActBase",  # pc-only
    0x2A591E4B: "cEmc3ActDamage",  # pc-only
    0x2A5D4D26: "rSoundSource::CHUNK_HEADER",
    0x2A5DFC82: "sRender::Pass",
    0x2A604ABC: "CFDATA",
    0x2A61075A: "sShader::MyDTI",
    0x2A63A6EE: "__vector4",
    0x2A63B5D7: "cEm8cDmgPinion",  # pc-only
    0x2A6D7879: "INTERRUPT_LINE",
    0x2A6EDFB6: "_XMSG_DETAILS_REQUEST",
    0x2A6FB030: "tCMotionVector_X9",
    0x2A708979: "XONLINECONTENT_HEADER",
    0x2A71CAAF: "_cpinfo",
    0x2A77ADCB: "cEm44ActAtckJump",  # pc-only
    0x2A7A2D6C: "cNetEm42Slime",  # pc-only
    0x2A818176: "uOm08ed_FirePump::cActFire",  # pc-only
    0x2A8A1D90: "_CEA861_DATA_BLOCK",
    0x2A8B8681: "ID07_DCP_LB_DATA_RETURN2",
    0x2A9194CE: "uEffectVFR::PTCL_MOVE_STATUS",
    0x2A93E328: "_VERIFY_BILLING_TOKEN_RESPONSE",
    0x2A98A14F: "_XPROFILE_ACTION_AUTO_CENTER_OPTIONS",
    0x2A992623: "sPrim::FUNC_PRIM_MODE",
    0x2A9ABBA6: "cTrans::BLENDSTATE",
    0x2A9AE20B: "cEmc3ActWait",  # pc-only
    0x2AA64625: "uOmEvade::cActWait",  # pc-only
    0x2AAA2D47: "cEm30ActSideStep",  # pc-only
    0x2AAF448E: "rEffectList::FLAG32",
    0x2AB043D9: "uOm0026::cActWait",  # pc-only
    0x2AB194EB: "LB_DISP1_PARAM",
    0x2AB3CC1B: "CPU_MST_REQ_ATTR",
    0x2ABB37DE: "RB_DEPTH_INFO",
    0x2ABC0DBB: "FSB_TX_PMC5_AND",
    0x2AC05CA0: "ID3DXPMesh::__vftable",
    0x2AC9AB36: "BIF_INT_VECTOR",
    0x2ACC7948: "uOm1307_Boat::cEventActWaiting",  # pc-only
    0x2ACD1930: "uColorCorrectFilter::Corrector",
    0x2ACF2A82: "_GET_LINKED_GAMERTAG_RESPONSE",
    0x2AD48D57: "sCollision::ScrColInfoBasic::MyDTI",
    0x2ADE4260: "_XCONFIG_POWER_VCS_CONTROL",
    0x2ADF3949: "sPrim::Vertex",
    0x2AE1CF27: "STREAMINDEXEDENUM",
    0x2AE2C410: "cEm83ActWalk",  # pc-only
    0x2AE31CA2: "cOmWindowAction_dive",  # pc-only
    0x2AEB09B0: "_DM_GAME_CONTROLLER_DATA",
    0x2AEB5EB4: "PCIE_CNTL",
    0x2AFC94F4: "NetworkRankingPat",
    0x2B006B4E: "XONLINE_FRIEND_INTERNAL",
    0x2B00C052: "uOma00e_UroWall::cActBase",  # pc-only
    0x2B055724: "BIOS_7_SCRATCH",
    0x2B0BA99E: "XAUDIOCHANNELMAPENTRY",
    0x2B0D5F97: "std::ios_base::_Iosarray",
    0x2B0EF590: "_XMSG_DETAILS_BLOB",
    0x2B11E9A3: "IDirectXFileDataReference",
    0x2B1478FF: "_BUFFERCACHEENTRY",
    0x2B153517: "_DXVA_ExtendedFormat",
    0x2B15B189: "PIX_REQUEST_GPU_CAPTURE",
    0x2B2295D1: "PA_CL_CLIP_CNTL",
    0x2B2346AA: "PCIEP_HW_DEBUG",
    0x2B2823CA: "_XGET_REVOCATION_LIST_REQUEST",
    0x2B2D3690: "_INSTRUMENTATION_UPLOAD_REQUEST",
    0x2B2DDAED: "cWpAction_wp30_act_light_put",  # pc-only
    0x2B2E5F8A: "SQ_2D_PIXEL_CONSTANT_2",
    0x2B38EFB4: "STATE",
    0x2B472059: "_XNQOSAGGREGATETYPE",
    0x2B4CD106: "_FPIEEE_EXCEPTION_FLAGS",
    0x2B50D9BF: "DCCG_DEBUG_02",
    0x2B59A9FA: "tUNCACHE_RELOC_CTL",
    0x2B5DB7AC: "IOC_PERFCOUNTER2_HI",
    0x2B638634: "cEm30ActDmgButtobi",  # pc-only
    0x2B7059E4: "_s__RTTIClassHierarchyDescriptor",
    0x2B711FBD: "MtAllocator::MyDTI",
    0x2B7A510F: "uToneMapFilter::MyDTI",
    0x2B7B4887: "cPlAction_pl_act_wall_crouch_on",  # pc-only
    0x2B7CE620: "_CHANGE_SUBSCRIPTION_PAYMENT_INSTRUMENT_REQUEST",
    0x2B810885: "MtEaseCurve",
    0x2B814965: "_IMAGE_FUNCTION_ENTRY64",
    0x2B815F33: "IPersistVtbl",
    0x2B82F93F: "_IMAGE_LINENUMBER",
    0x2B845EBF: "PERF_MAX_BSB_READ_LATENCY",
    0x2B858CF3: "uEffectEdit::GEN_STATUS",
    0x2B8F51D2: "_XONLINE_STATS_ENUM_BY_USER_REQUEST",
    0x2B93BDF7: "IClassFactory",
    0x2B93C3EB: "_DXVA_COPPCommand",
    0x2B943DA2: "rMovieOnMemoryInterMediate::MyDTI",
    0x2B950986: "ID3DXSaveUserDataVtbl",
    0x2B9ACC74: "uModel::Motion::MyDTI",
    0x2BA02704: "PCIE_RX_TLP_HDR2",
    0x2BA223A3: "cFSMRelate",  # pc-only
    0x2BA3894D: "uOm0912_s119Tram::cActReady",  # pc-only
    0x2BA3CEA1: "_XSTORAGE_ENDPOINT",
    0x2BB0D4A4: "GPUALUSCALAROP",
    0x2BB2A3EF: "IOC_BSB_SLV_REQ_CRC_2",
    0x2BB5F75F: "_XUIBRUSH",
    0x2BBB2F10: "ID11_LUT_DATA_B",
    0x2BC0CC47: "uRadialBlurFilter::MyDTI",
    0x2BC13055: "cEm4502ActWait",  # pc-only
    0x2BC6984B: "uOm092e_LaserBlock::cActBase",  # pc-only
    0x2BC7A394: "rEffectSetData::ESD_SET_TEXLINE",
    0x2BCDD11E: "cEm32PlEvent_MountFinish",  # pc-only
    0x2BCFA78D: "XAUDIOVOICEPROCESSCALLBACK",
    0x2BD599C9: "REG_MACRO_DATA_2",
    0x2BD66C34: "FSB_TLA_PATT_CARE_MASK1",
    0x2BD76D8E: "SQ_CONSTANT_0",
    0x2BE09544: "cNetEm6d",  # pc-only
    0x2BE16716: "GC_VENDOR_ID",
    0x2BE172BF: "cEm44PlEvent_Entwine",  # pc-only
    0x2BE20270: "XMEDIA_CREATE_TYPE",
    0x2BE44187: "CP_RT1_BADR",
    0x2BE46D19: "cHitParam",  # pc-only
    0x2BE4A65D: "cEm22ActAtkCutting",  # pc-only
    0x2BE4BC5B: "AZ1_MRU_BANK2_DEPTH_MASK",
    0x2BE57A82: "_Collvec",
    0x2BE7762D: "cEm43ActCatchKill",  # pc-only
    0x2BE8A690: "cEm20ActAtkExecKill_PL",  # pc-only
    0x2BE9AD3F: "EP_IOC_HARD_RESET",
    0x2BEA3D33: "cEm10ActRoll",  # pc-only
    0x2BF86BC0: "NetworkLayer::SiblingList",
    0x2C02253A: "rEffectSetData::ESD_PARAM_COLL",
    0x2C1054CB: "PCIE_TX_SEQ",
    0x2C14F69E: "EP_UNUSED_BAR_3",
    0x2C1670A9: "_ACCESS_DENIED_OBJECT_ACE",
    0x2C1999F7: "NetworkXboxVoice",
    0x2C1A61A6: "D1MODE_VLINE_STATUS",
    0x2C1B1F94: "cOma016ActCut02",  # pc-only
    0x2C1BC089: "_STRING_VERIFY_2_REQUEST",
    0x2C1FF34F: "CP_ME_CF_EVENT_ADDR",
    0x2C207660: "cEm84PlEvent",  # pc-only
    0x2C218114: "PCIE_UNCORR_ERR_SEVERITY",
    0x2C21CD43: "SQ_CONSTANT_RT_2",
    0x2C236BF2: "MC0_STATUS_0",
    0x2C282712: "cSubAction::Base",  # pc-only
    0x2C2DC5BF: "uOm1317_Glass::cActBase",  # pc-only
    0x2C3DB165: "sLight::MyDTI",
    0x2C40D1F7: "cEma2ActMogaku_PL",  # pc-only
    0x2C429EA5: "rEffectSetData::RANGE_OPTION_FLAG",
    0x2C452A3F: "VGT_HOS_MAX_TESS_LEVEL",
    0x2C45F03A: "rArchive::DecompressStream::MyDTI",
    0x2C46B4B2: "rEffectList::KEYFRAME_INP_TYPE",
    0x2C46C2F0: "uOma004_Collapse::cActWait",  # pc-only
    0x2C48C95F: "_P_CANCEL_MSG",
    0x2C4ABBDF: "XECRYPT_DH_1024",
    0x2C4CEBD1: "MtObjectGroup",
    0x2C4D09C8: "cEm10ActAtkGunShotGG",  # pc-only
    0x2C51BF5D: "XUIMessageItemOverride",
    0x2C544EA4: "sToolBase::__vftable",
    0x2C5570A5: "uOm095e_Kick::cActBase",  # pc-only
    0x2C558540: "MOT_TYPE",
    0x2C5805B7: "cOmCoopBoxAction_pl_act_push_end",  # pc-only
    0x2C5854A5: "ID06_DCP_LB_DATA_RETURN1",
    0x2C5B380A: "XCOMPRESS::_LZXCOMPRESSION_CONTEXT_HEADER",
    0x2C660894: "XUINotifySelChanged",
    0x2C6DE13B: "XG_MCT::CodeType",
    0x2C6F4255: "rEffectSetData::REACTION_TYPE",
    0x2C730D3F: "SQ_THREAD_ARB_PRIORITY",
    0x2C7692C5: "rEffectSetData::ESD_SET_CULL_POLYLINE",
    0x2C79150A: "cEm42ActRound2Enter",  # pc-only
    0x2C8129CC: "aS109::cActEvJeepBikeAppear",  # pc-only
    0x2C8391A4: "cSetInfoOmLoadItem",  # pc-only
    0x2C8424C4: "CP_PERFMON_CNTL",
    0x2C901D67: "cPlAction_pl_act_damage_chair",  # pc-only
    0x2C931868: "STREAMDEPREC",
    0x2C98A392: "WAIT_UNTIL",
    0x2C9D9246: "XUIMessageControlNavigate",
    0x2C9F3D62: "D3DXps",
    0x2CA3A648: "GPUENDIAN",
    0x2CA47662: "GPUCmdIntComp",
    0x2CA50ADD: "cEm10ActDemoGatling",  # pc-only
    0x2CADD823: "rSoundDirectionalCurveXml::MyDTI",
    0x2CAF77D7: "_DM_SETTINGS",
    0x2CB21F4D: "CCalWmaDecoder",
    0x2CB7E194: "_XMATCH_SESSION_SPLIT_REQUEST",
    0x2CB80074: "uIdTutorial00",  # pc-only
    0x2CB85DD0: "REG_MACRO_DATA_6",
    0x2CBABCB0: "cOmBoatAirAction_om_act_die",  # pc-only
    0x2CBBFAEE: "_D3DSAMPLER_TEXTURE_TYPE",
    0x2CC39219: "uOma00b_LaserArea::cActBase",  # pc-only
    0x2CC53994: "uEffectVFR::MassBillboard",
    0x2CCBBD30: "BIU_INT_BAD_IOC_READ_ADDR",
    0x2CCEBD8E: "XAUDIORENDERFXCALLBACK",
    0x2CD2D4BF: "CFRESERVE",
    0x2CE08CE1: "cEm63ActDmgAir",  # pc-only
    0x2CE59F8B: "MtCollada::Code",
    0x2CE688B1: "XAUDIO::CRoutedVoice::__vftable",
    0x2CE69335: "Q_MESSAGE_NOTIFICATION",
    0x2CEBCF08: "IOC_FUSE_OVERRIDE",
    0x2CEC446F: "CP_IB2D_BASE",
    0x2CF130AA: "MtUI",
    0x2CF6FD43: "cAITerrainNearCornerAnalyzer",  # pc-only
    0x2CF887F1: "_CONTENT_DETAILS_RESPONSE",
    0x2CF8C1E9: "ID3DXBufferVtbl",
    0x2D06119E: "BIU_PERFCOUNTER1_HI",
    0x2D0CC4A2: "uEffect2D::LifeFrame",
    0x2D126024: "LB_DISP1_REQ",
    0x2D12C5BD: "sCollision::CALLBACK_MODE",
    0x2D12E086: "rSoundRandom",
    0x2D135BC3: "ID3DXBaseEffect",
    0x2D14C334: "sLightLinker::TVNoise",  # pc-only
    0x2D158177: "CP_BIN_MASK_LO",
    0x2D1947A5: "rModelMontage::MyDTI",
    0x2D1D7C9F: "uOm1316_BackupHeli::cActMove",  # pc-only
    0x2D1D81A8: "PCIE_PERF_COUNT1_TXCLK",
    0x2D25091A: "type_info::__vftable",
    0x2D2611E7: "CRTC_DOUT_INTERFACE_02_DEBUG",
    0x2D2807F6: "XAUDIOCHANNELVOLUMEENTRY",
    0x2D34E86C: "RB_COPY_DEST_PITCH",
    0x2D354A68: "tagLOCKTYPE",
    0x2D3AC17A: "cEm66ActSwimBiteDemo",  # pc-only
    0x2D3CF361: "sShader::FUNC_SHADOW_PCF",
    0x2D4072DA: "rCollision::Node",
    0x2D49F0AF: "MtREDataWriter",
    0x2D4AC127: "_HEAP_ENTRY_EXTRA",
    0x2D52ADA1: "_XNOTIFICATION_SEND_DEQUEUE",
    0x2D55BA4C: "uOma004_Collapse::cActActBtn",  # pc-only
    0x2D55E4B5: "SPLL_CNTL_REG",
    0x2D563269: "DC_PERFMON_CNTL",
    0x2D57AFA2: "CBaseEndianBuffer",
    0x2D590566: "_P_TEAM_CREATE_MSG",
    0x2D59CE28: "_XONLINE_FRIEND",
    0x2D6F5379: "D1OVL_CONTROL1",
    0x2D703329: "CP_RT2_BADR",
    0x2D725170: "_EALARM",
    0x2D73A78E: "D3D::CMicrocodeBuilder",
    0x2D74AA3B: "uOma004_Collapse::cActGoal",  # pc-only
    0x2D76747B: "XUIMessageNavForward",
    0x2D7723E5: "cEm71ActErase",  # pc-only
    0x2D775A62: "_PORT_MESSAGE",
    0x2D7A5C98: "CODECSPECIFICDATA",
    0x2D7C40E5: "D1CRTC_FORCE_COUNT_NOW_CNTL",
    0x2D7E6C29: "tagRandState",
    0x2D83C9A5: "uOm092e_LaserBlock::cActPlBase",  # pc-only
    0x2D83E9C7: "cEm10ActAtkKick16",  # pc-only
    0x2D878768: "PCIE_RX_CREDITS_RECEIVED_CPLD",
    0x2D8B86FB: "D1GRPH_FLIP_CONTROL",
    0x2D8C4DE7: "cTrans::RV_FLAGS",
    0x2D92F860: "IDirectXFileBinary",
    0x2D931E00: "XConfigStatisticSettings",
    0x2D935B51: "RB_TILE_CLEAR",
    0x2D97E7DC: "cEm30ActSnarlBgn",  # pc-only
    0x2D9CBED6: "SB_SUB_CLASS",
    0x2D9D3E0D: "uMirror::MSAA",
    0x2DA6CA2C: "rFacialAnimation::FANIM_HDR",
    0x2DA8B992: "CCalBase::ALLOCATION_TYPE",
    0x2DA93C54: "XMESSAGING_MSG",
    0x2DB24A93: "_XEIKA_CERT_OVERLAY_ELEMENTS",
    0x2DB3FC20: "_OBJECT_ATTRIBUTES",
    0x2DB46564: "cEm40ActThreat",  # pc-only
    0x2DB82CB7: "_XSTATS_RESET_REQUEST",
    0x2DBB8623: "uToneMapFilter::TMATTR",
    0x2DBDA3E5: "IOC_BSB_MST_REQ_CRC_0",
    0x2DC19AE8: "_XENUMERATORCONTENTOFFER",
    0x2DC310A4: "WMMESSAGESTRUCT",
    0x2DC402D0: "_XGCPUSHADERCONTEXT",
    0x2DC42081: "tWMAParseState",
    0x2DC54131: "rCloth",
    0x2DD10B2B: "FSB_LX_PMC3_OR",
    0x2DD2A208: "uModel::RenderInfo",
    0x2DD4036F: "cEm10ActAtkSpearBigStart",  # pc-only
    0x2DD8B243: "uShadow::LEGACY_SHADOW_TYPE",
    0x2DD9C7C1: "_XUSER_STATS_ROW",
    0x2DDE37F9: "cPositionFilterRangeAroundPlayerPos",  # pc-only
    0x2DDEEBBC: "_QUERY_UPDATE_REQUEST",
    0x2DE40857: "VGT_DEBUG_REG1",
    0x2DE86AE3: "XAUDIO::CFastSpinLock",
    0x2DEA51D3: "AZ0_PRIMARY_STATE_DWORD1",
    0x2DEA6D70: "rAIWayPoint::Node",  # pc-only
    0x2DEB1DB7: "XUIMessageGetSetVisualPrefix",
    0x2DF43A6F: "_XCONFIG_STATISTIC_ENTRIES",
    0x2DF87183: "t_g726state",
    0x2DFB460D: "tagWMSDKRESIZER",
    0x2E000C21: "cArea::__vftable",
    0x2E02B5D0: "cEm10ActHangWall2",  # pc-only
    0x2E07233B: "cAIDynamicPathFinding::UnitManagement",  # pc-only
    0x2E0BBED6: "_XMMATRIX",
    0x2E0E59F3: "tagWMVAVSyncState",
    0x2E0F7D27: "FSB_LX_DDAT0",
    0x2E0FC0AE: "VC_PERFCOUNTER2_LOW",
    0x2E10D3D8: "std::_Iterator_base",
    0x2E19A993: "XDVO_CONTROL",
    0x2E19B1A7: "D1CRTC_OVERSCAN_LEFT",
    0x2E1AF264: "uOmElevator::cActPlWait",  # pc-only
    0x2E1BF920: "sCollision::GetTriangleInfo",
    0x2E1E43D8: "std::ios_base::_Fnarray",
    0x2E24857F: "TCM_PERFCOUNTER0_LOW",
    0x2E2712F8: "_XUSER_PRIVILEGE_MSG",
    0x2E3091D4: "XUICustomPropHandler",
    0x2E30F8C4: "MtCollada::Animation",
    0x2E317B6D: "D3D::LazyState",
    0x2E33501D: "sPrim::FRect",
    0x2E34EFD2: "D3DXVECTOR2_16F",
    0x2E3524D8: "rScheduler::HEADER",
    0x2E3D4817: "cOm0200Action",  # pc-only
    0x2E3DB9F7: "XnSockInfo",
    0x2E3DE9E5: "cEm34Action",  # pc-only
    0x2E3FE9DB: "sSoundN::Entry",
    0x2E40EC34: "D3D::XBMContext",
    0x2E424595: "PCIE_INDEX",
    0x2E45BC04: "_FPIEEE_PRECISION",
    0x2E4A1E54: "_D3DTEXTUREFILTERTYPE",
    0x2E4FB086: "cEm32ActGroundToWall",  # pc-only
    0x2E5B69DC: "PCIE_PERF_COUNT0_SLV_S_C_CLK",
    0x2E60C5BF: "rSoundCurveXml::Curve",
    0x2E616308: "CP_RT7_COMMAND",
    0x2E61D159: "GPUPERFEVENT_RBBM",
    0x2E6FA0DE: "_TOKEN_STATISTICS",
    0x2E72E99F: "MC0_PAD_CAL_CNTL",
    0x2E742906: "tagWMAFileContDesc",
    0x2E759C64: "sCollision::CONTACT_MODE",
    0x2E7AD5E5: "D3DVolume",
    0x2E7D9202: "_XDIRCRAWL_STATE",
    0x2E804724: "sGpuParticle",
    0x2E822F2E: "CP_RT10_SIZE",
    0x2E826F86: "D3DXpsThread",
    0x2E840D87: "cEm6cActEscape",  # pc-only
    0x2E84DA60: "cAIPositionPickUpObject",  # pc-only
    0x2E85A59C: "cNetEm66",  # pc-only
    0x2E870F22: "cEm6fActDestFly",  # pc-only
    0x2E8B0D1A: "sNetworkLibrary::TinyDate",
    0x2E8C8C49: "_XSESSION_INFO",
    0x2E92FC6C: "XAUDIO::XAUDIOFXMGRFXTABLEENTRY",
    0x2E9CC0C2: "ID3DXFragmentLinkerVtbl",
    0x2EA10CEB: "MtObject",
    0x2EA5903B: "MtCriticalSection",
    0x2EA795D6: "_HVPOWER_INFO",
    0x2EA92566: "MtProperty::Custom",
    0x2EAECAFB: "_STFC_CONTROL_CODE",
    0x2EB0180D: "_XARB_REPORT_REQUEST",
    0x2EB5870C: "_DXVA_MBctrl_I_HostResidDiff_1",
    0x2EB5FB19: "WeightMode",
    0x2EBA9C6B: "MtCollada::Mesh::MyDTI",
    0x2EC01EAE: "cGoalPos",  # pc-only
    0x2EC3589F: "rEffectSetData::ENTRY_TYPE",
    0x2EC3D143: "uIdChapSt00",  # pc-only
    0x2ECA8076: "cOmJeepAction_om_act_die",  # pc-only
    0x2ECB9B68: "XAUDIO::XAUDIOPACKETCTX",
    0x2ECF30A6: "NetworkCommunityLive::moveGetAccountSelfCountry::__l3",
    0x2ED01DF4: "NetworkLayer::ChildList",
    0x2ED1A340: "uScheduler",
    0x2ED47FDC: "sCollision::TriangleInfo",
    0x2ED58CC4: "rEffectList::COLOR_CORRECT_TYPE",
    0x2EDDB256: "D1CRTC_INTERLACE_CONTROL",
    0x2EE33B97: "cEm83ActRun",  # pc-only
    0x2EE394CB: "LIVEBASE_CONTENTAVAILABLE_MSG",
    0x2EF22EF7: "_FSCACHE_PROCESS_TYPE",
    0x2EF24DAA: "_IDE_SECURITY_DATA",
    0x2EF3AAB9: "MtCollada::Scene::MyDTI",
    0x2EFC6026: "cEm10ActSideJump",  # pc-only
    0x2EFD73EE: "uOma004_Collapse::cActPlSuccess",  # pc-only
    0x2EFFBA9C: "cEm70ActDieIce",  # pc-only
    0x2F004662: "cPlAction_pl_act_attack_upper",  # pc-only
    0x2F037DB2: "sPrim::TexCoord",
    0x2F07EA11: "CXLiveAsyncTaskInternal::REQUESTTHROTTLEDATA",
    0x2F0BA083: "CCalRenderer::__vftable",
    0x2F0DB985: "NetworkSessionManagerLive::moveLeaveSessionCommon::__l2",
    0x2F0F687B: "_ABCH_GET_CONTACTLIST_GAMERTAGS_REQUEST",
    0x2F117848: "cEm83ActDmgBlowS",  # pc-only
    0x2F1848F4: "CRTC1_DEBUG_07",
    0x2F1985E5: "NetworkLayer::MemberReceive",
    0x2F1AD25A: "GPUSCREENEXTENTS",
    0x2F2494A4: "cOmRider2ActDmgR",  # pc-only
    0x2F2568B1: "cEm70ActDie",  # pc-only
    0x2F260B87: "TP2_PERFCOUNTER0_SELECT",
    0x2F2E7FC0: "cEm80ActSyutoEscRoll_PL",  # pc-only
    0x2F2FA649: "PCIE_TX_REPLAY",
    0x2F303BA4: "FSB_LX_PHYREAD",
    0x2F30C233: "LOTAreaList",  # pc-only
    0x2F333322: "NetworkLayer::Property",
    0x2F4652A2: "rEffectSetData::ESD_SET_LIGHT",
    0x2F50C130: "DC_SURFACE_0_BASE",
    0x2F50E6A1: "GPUTEXTURESIZE_2D",
    0x2F527708: "cEm44ActToDown",  # pc-only
    0x2F529958: "cPlAction_pl_act_wall_stick_t_ready",  # pc-only
    0x2F52E684: "D3DStateBlock",
    0x2F57C820: "cOmBoatAirAction_pl_act_change_cancel",  # pc-only
    0x2F58617B: "PA_CL_VPORT_XSCALE",
    0x2F5A6162: "cEm84ActAtckHiKick",  # pc-only
    0x2F5D74BF: "_UPDATE_PAYMENT_INSTRUMENT_REQUEST",
    0x2F616A91: "cOmCoopDoorAction",  # pc-only
    0x2F6D7ABA: "COHER_STATUS_HOST",
    0x2F6DFC45: "cPositionFilterRangeAroundPos",  # pc-only
    0x2F72A5DD: "sLight",
    0x2F750FE7: "uOmS705ceil::cActStopEm",  # pc-only
    0x2F753119: "MtCollada::Joints::MyDTI",
    0x2F7C2708: "cEm84ActSitOnHandrail",  # pc-only
    0x2F7D0746: "SUBFRAME_PARAM_SC",
    0x2F80A80B: "ISOFileTypeAtom",
    0x2F8CCD55: "D1GRPH_ENABLE",
    0x2F8D4A71: "rModelMontage::TYPE",
    0x2F8DE397: "MtGeomRay",
    0x2F96D697: "D3D::ParseData",
    0x2F97861B: "uEffectVFR::Light",
    0x2FA2845A: "uEffectVFR::CHAIN_STATUS",
    0x2FA61E4A: "D3DVertexBuffer",
    0x2FA7AB91: "_ACCOUNT_ACCEPT_TOU_REQUEST",
    0x2FA80921: "_XCONFIG_DVD_SETTINGS",
    0x2FAAB24F: "XECRYPT_RSAPRV_1024",
    0x2FAD1AC5: "uModelEdge::BLEND_TYPE",
    0x2FAEE73D: "rEffect2D::E2D_KEYFRAME_COLOR",
    0x2FB54E26: "sPhysics::Constraint",
    0x2FB77BDE: "tagWMAFileChannels",
    0x2FB9EFE4: "TC_CNTL_STATUS",
    0x2FBDB57E: "sResource::MyDTI",
    0x2FBEC22E: "SKIPBITCODINGMODE",
    0x2FC145C0: "cSystem::MyDTI",
    0x2FC39984: "MSI_MSG_ADDR_LO",
    0x2FC890A4: "XAUDIO::CSourceVoice::__vftable",
    0x2FC948B2: "BITMAPINFOHEADER_BITFIELDS",
    0x2FCEBE59: "uOm08b3_S203Elev::cActRiseEnd",  # pc-only
    0x2FCED075: "MtCollada::Entry::MyDTI",
    0x2FD400B4: "_XUSER_ESTIMATE_RANK_RESULTS",
    0x2FD6616E: "rIni",  # pc-only
    0x2FD732F2: "uTVNoiseFilter::trans::__l9::SCREEN_VERTEX",
    0x2FDF93EF: "cEm45ActDeathAtk",  # pc-only
    0x2FE42B89: "cEm43ActShakeAttack",  # pc-only
    0x2FE4DAD3: "tagWMVStartCodeIndex",
    0x2FE96CFA: "rSoundStreamRequest::MyDTI",
    0x2FEDAE6A: "_FILE_FS_ATTRIBUTE_INFORMATION",
    0x2FEF6231: "CXuiModule::__vftable",
    0x2FF3CE11: "_PPC_INSTRUCTION",
    0x2FF47E3D: "PCIE_P_PHY_DEBUG",
    0x2FFD7B11: "cEm32ActDmgFallWall",  # pc-only
    0x2FFED7B6: "XG_MCT::CSimpleEncodeModel",
    0x2FFF5013: "FRAME_UNWIND_NESTED_FRAMES",
    0x300314BB: "DSMEMTRACK",
    0x300578F6: "FSB_TX_PMC1",
    0x30063392: "FSB_LX_PMC4_OR",
    0x30063D4E: "cEm20ActDmgKneelDown",  # pc-only
    0x300693DB: "cEm42CAct2ndBlow",  # pc-only
    0x300752CE: "rCameraListXml::CameraInfo",
    0x30131406: "_XONLINE_STATS_COLUMN",
    0x30152560: "_XSESSION_STATE",
    0x301CAB8E: "uInteractiveWater",
    0x30207DFD: "CP_DMA_COMMAND",
    0x3021D2A2: "cEm0cPlEvent_Escape",  # pc-only
    0x30240C18: "_XCONTENT_METADATA_INSTALLER_PROGRESS_CACHE",
    0x30244F30: "_PCMData",
    0x302456E6: "PCIE_PERF_CNTL_TXCLK",
    0x3027AA86: "NetworkRankingLive::moveGetRankingScoreListByUniqueId::__l3",
    0x30281234: "uWater::MyDTI",
    0x302A3516: "_XUPDATE_REFERRAL_REQUEST",
    0x302CCEED: "_XEX_IMPORT_TABLE",
    0x303537DA: "LtRtDownmix",
    0x3036F48A: "rGridEnvLight::__vftable",
    0x30390A5A: "XECRYPT_ECPUB_512",
    0x303BD816: "cEm34ActDamage",  # pc-only
    0x303CEE26: "uAdhesion::ADHESION_INFO",
    0x30400C9A: "PCIE_P_PLL_CNTL",
    0x3040585B: "_Cvtvec",
    0x3041A995: "_PRESENCE_GET_STATE",
    0x3041F034: "AZ1_MRU_BANK3_DEPTH_MASK",
    0x3043D3AB: "TCF_PERFCOUNTER11_LOW",
    0x3046D04F: "PA_SC_WINDOW_OFFSET",
    0x30470848: "uProjectionShadow::MyDTI",
    0x304D5908: "_s_CatchableType",
    0x304EAD52: "cAIWayPoint",  # pc-only
    0x304FA1E0: "MP4CopyrightAtom",
    0x305016B3: "uEffectEdit::PTCL_MOVE_STATUS",
    0x3053CFDF: "D3DVolumeTexture",
    0x305AC309: "D3D::ParameterEnum",
    0x305D7186: "CP_2D_IMMD_BASE",
    0x30620E1E: "TCF_PERFCOUNTER9_HI",
    0x3063C02A: "_HV_IMAGE_IMPORT_TABLE",
    0x3066A80D: "rShader::PARAMETER_INFO",
    0x306948AA: "uModel::Constraint::__vftable",
    0x306B7794: "sAI",  # pc-only
    0x306C1BCB: "_EMB2PASS",
    0x30750391: "CP_RT5_BADR",
    0x307F2F3B: "_D3DBOX",
    0x307FC931: "ID3DXPatchMeshVtbl",
    0x3083730B: "uOmSpileTrap::cActWait",  # pc-only
    0x3084B271: "rEffect2D::E2D_PARTICLE_LINE",
    0x3086C5E8: "D1MODE_MAX_CHUNK_SIZE",
    0x3087ACA4: "_CEA861_VENDOR_SPECIFIC",
    0x3088C9EE: "D3DXFLOAT16",
    0x308DABAC: "cEm41ActPunchCancel",  # pc-only
    0x3096C4A3: "XAUDIO::CRiffChunk",
    0x30972CFB: "cOmRider2Action",  # pc-only
    0x3099AEAF: "_DXVA_PictureParameters",
    0x309A4E32: "GPUPERFEVENT_TCR",
    0x30A3ECF2: "cOmCoinActDamage",  # pc-only
    0x30A93D9A: "HeapManager::Block",
    0x30AB0849: "rCloth::AxisType",
    0x30B172E5: "sCollision::TriContactStackData",
    0x30B9C772: "uOm1307_Boat::cActWait",  # pc-only
    0x30C07189: "uCloth",
    0x30C5FA11: "MtGeomAABB",
    0x30C8E619: "XUIMessageNavInfo",
    0x30C9A445: "GPUVERTEXFETCHOP",
    0x30CBA64F: "_KD_PHYSICAL_PORT",
    0x30CDCAAB: "uOm1316_BackupHeli2::cEvActBase",  # pc-only
    0x30D0CAB4: "_GET_USER_SUBSCRIPTION_DETAILS_RESPONSE",
    0x30D20EC9: "FSB_TLA_ACTION_CONTROL",
    0x30DAEC60: "PCIE_TX_CREDITS_LIMIT_CPLD",
    0x30DBDC1F: "_DXVA_FilmGrainCharacteristics",
    0x30DD1B7A: "_RTL_HEAP_USAGE_ENTRY",
    0x30E1303F: "cNetEm61",  # pc-only
    0x30E3B453: "uOm090d_Floor::cActStop",  # pc-only
    0x30E71356: "rEffectSetData::ESD_SET_POLYLINE",
    0x30E7961E: "uOma00c_UroAction::cActActorAct",  # pc-only
    0x30EC6B70: "MP4DegradationPriorityAtom",
    0x30ED05E8: "_DXVA_PicParams_H264",
    0x30ED4060: "rPath",  # pc-only
    0x30EE55DC: "XAUDIO::CResampler",
    0x30F5E09B: "_XCONTENT_TRANSFERFLAGS",
    0x30F80B17: "cEm60ActDmgIce",  # pc-only
    0x30F8D05D: "_D3DRESOURCETYPE",
    0x30F9CBB9: "XDVO_CRC_CNTL",
    0x30FC8819: "TP3_PERFCOUNTER0_SELECT",
    0x30FD0150: "cPos",  # pc-only
    0x3101A0EE: "sLightLinker::uLinker",  # pc-only
    0x31031429: "DIRECTCOLORCONVFRM",
    0x3103B376: "COHER_BASE_RT",
    0x31040E8A: "cOmCoopBoxAction_om_act_ready",  # pc-only
    0x3105A601: "PIX_CHUNK_HEADER",
    0x3107127D: "CCalCddaStream",
    0x310754AD: "BIOS_13_SCRATCH",
    0x310A34AC: "GPUCOPYSRCSELECT",
    0x310A60D2: "uMirror",
    0x310C83D1: "cPlAction_pl_act_avoid_crouch_out",  # pc-only
    0x310F4537: "_D3DCOUNTER",
    0x311853C5: "FXLEffect",
    0x31198BAD: "_XLIVEBASE_GET_TASK_PROGRESS",
    0x311BDA12: "XCOMPRESS::t_decoder_context",
    0x3121B97D: "BIU_INT_STATUS",
    0x31221104: "MP4ChunkOffsetAtom",
    0x312653EA: "std::locale::facet",
    0x312EB7DD: "uFilter::PASS",
    0x313180B6: "_XVIDEO_MODE",
    0x31393192: "GPUFILLMODE",
    0x313C6561: "D3D::DebugAllocation",
    0x313DE1A2: "sApp::LANGUAGE",
    0x314074BB: "XShaderPDBHint",
    0x3143496D: "cEm20ActWalk",  # pc-only
    0x31458E18: "PIX_INDEXER_STATE",
    0x3145A084: "pcmwaveformat_tag",
    0x314664E7: "_DXVA_PicEntry_H264",
    0x314BB205: "XUIMessageGetBounds",
    0x31536E0B: "_XSESSION_REGISTRATION_RESULTS",
    0x3161A73A: "XUIMessageSourceHtml",
    0x3165FDB0: "MC1_DLL_MASTER_ADJ_1",
    0x3166029E: "cAIFSMAgent",  # pc-only
    0x31660850: "cEm84PlEvent_Catch",  # pc-only
    0x316633B6: "XAUDIO::XAUDIOROUTEDVOICEINIT",
    0x3166BCD0: "_D3DXIMAGE_FILEFORMAT",
    0x31693686: "IXuiTexture::__vftable",
    0x3169A3B7: "CP_ME_PS_EVENT_ADDR",
    0x316B443B: "RB_HSIO_DLL_INIT",
    0x3170DC84: "MtObjectGroup::__vftable",
    0x31743660: "uLightShaft",
    0x31793FF0: "VGT_DMA_SWAP_MODE",
    0x317AB4ED: "rSoundSourceEnvironmentInterMediate",
    0x3187050B: "MC0_CNTL",
    0x31876296: "MtCollisionEpa::MtEpaLocalList",
    0x318B4714: "rEffectAnim::MyDTI",
    0x318B50E0: "MP4UserDataRecord",
    0x318D1FA7: "VGT_HOS_REUSE_DEPTH",
    0x318EFFFE: "uOm0927_Crane::cActMoveInit",  # pc-only
    0x3194A413: "uEffectVFR::Texline",
    0x31962E19: "D3DXPLANE",
    0x319B7FD6: "PCIE_RX_CNTL",
    0x319BCDDE: "FSB_TX_TERST_XSTP_AND",
    0x319CE9E4: "ID3DXPatchMesh::__vftable",
    0x31A01AA0: "rVibration::MyDTI",
    0x31A63CFD: "XUIMessageItemCount",
    0x31A7E8B0: "_HEAP_PSEUDO_TAG_ENTRY",
    0x31A950D0: "cWpAction_wp_act_throw",  # pc-only
    0x31AD4835: "cArea",
    0x31B179B1: "NetworkSessionManagerBroadcast::ManagementMessageInfo",
    0x31B31435: "ID3DXBuffer::__vftable",
    0x31B3AA1C: "CXContentDownloadMedia::FIND_MEDIA_INSTANCE_URLS_RESPONSE_BUFFER",
    0x31B74788: "cEm65ActDie",  # pc-only
    0x31B7D386: "cAIFSMManager::ActionInfo",  # pc-only
    0x31B8C462: "_FP_OPERATION_CODE",
    0x31C56DF7: "_QUERY_FINDFROMIDS_REQUEST",
    0x31C79DDC: "uOmClutch::cActWake",  # pc-only
    0x31C7D197: "XCODEC_TYPE",
    0x31C83F5C: "CCalAudioRenderer::CreateParameters",
    0x31C8F506: "IXAudioBatchAllocatorVtbl",
    0x31C9DD95: "FSB_LX_PMC3_AND",
    0x31CDFA6E: "XGI_WRITEGAMERTILE_MSG",
    0x31CEE3D8: "cWpAction_wp_act_dummy",  # pc-only
    0x31D52CED: "cLinkUnit::cTarget",  # pc-only
    0x31D7A2B8: "cTrans::Element::ATTR",
    0x31D8182A: "CRTC_DEBUG",
    0x31D9DD3E: "MEDIATYPE",
    0x31DC1FF8: "rSoundPackageXml::SplitData",
    0x31E2D0D3: "FSB_LX_CTRL_OR",
    0x31EA6FF3: "cEm66ActDive",  # pc-only
    0x31EE71EE: "cTrans::ArrayTexture::MyDTI",
    0x31F24CA7: "cFSMOrder::FuncParamKillEnemy",  # pc-only
    0x31F693D6: "rMovieOnDisk",
    0x31F8026D: "sCollision::RequestPacket",
    0x31F8BAEB: "cEm34ActAtkCatch",  # pc-only
    0x31F9F9FE: "XECRYPT_SHA256_STATE",
    0x31FA0E67: "_IMAGE_BOUND_FORWARDER_REF",
    0x31FB1957: "_XONLINE_STATS_ENUM_RESULTS",
    0x31FD2B86: "rEffectList::EFL_PARAM_CHAIN",
    0x3204FE33: "_DISPLAY_INFORMATION",
    0x3207D421: "rAIPositionEvaluationFuncListXml",  # pc-only
    0x32080D74: "std::basic_istream",
    0x3209A232: "tagRECT",
    0x320DDB49: "rSoundDirectionalSet::Element",
    0x320E949A: "uOmUseItem::cActBase",  # pc-only
    0x3211A59A: "_RTL_PROCESS_HEAPS",
    0x32187E28: "_XPROFILE_GAMER_DIFFICULTY_OPTIONS",
    0x321E43D1: "MICPROXY",
    0x322245A6: "GPUPIXCENTER",
    0x322590EE: "MtCollision::SimplexSolver",
    0x3226C957: "cEm40ActWait",  # pc-only
    0x32270E30: "SQ_2D_PIXEL_CONSTANT_1",
    0x322A90D3: "cPlAction_pl_act_coop_jump_up_4m_first",  # pc-only
    0x3233671A: "positional_param",
    0x3235BAF3: "cEm82ActEvent_PL",  # pc-only
    0x3245FE2D: "BRTLBINBUFDATA",
    0x3245FE47: "_XMSG_USER_INFO",
    0x324AFC9B: "_PASSPORT_GET_USER_DATA_REQUEST",
    0x324E17E9: "cEm30ActDmgDown",  # pc-only
    0x32598805: "DCCG_DEBUG_01",
    0x325A4D6C: "MtDataWriter::Frame",
    0x325A839F: "MtGeomConvex",
    0x325AAF5B: "CP_VIP_EOL_EOF_COUNTER",
    0x32608C4A: "_RECOVER_ACCOUNT_REQUEST",
    0x3261A0A7: "sCamera",
    0x3261DF4B: "uPointCubeMapLight",
    0x3261E043: "PA_CL_VTE_CNTL",
    0x32646084: "rEffectSetData::RANGE_DIRECTION_TYPE",
    0x3265E2A0: "sSoundN::MultiBandEQBaseUnit::EQUnit",
    0x326951DA: "sRender::CAPS::RT_FORMAT",
    0x326A116D: "D3D::CCapture",
    0x326E03B3: "MtGeomTriangle::CoGIdResult4",
    0x326EF28B: "rEffectList::EFL_PARAM_CULLING",
    0x326EFB03: "XUIMessagePressState",
    0x3270633D: "EP_UNUSED_BAR_4",
    0x3272B0A3: "rCameraXml::MyDTI",
    0x32733EAF: "std::_Ranit_base",
    0x3275580B: "_DXVA_DeinterlaceTech",
    0x327A0394: "MtGeomRay::MyDTI",
    0x327C456A: "NetworkStorage",
    0x327E0E3B: "XAUDIOPIXCOUNTERS",
    0x327F8A37: "cOma016ActCut05",  # pc-only
    0x328A67BC: "uOmPlCopy::cActWait",  # pc-only
    0x328DDBDB: "MC0_SECURE_MEMORY_APERTURE_LOG_MH",
    0x328F5384: "MtCollada::Shader::MyDTI",
    0x3292CECC: "uBioActorPlayer",  # pc-only
    0x329341D9: "rConfig::MyDTI",
    0x329384C0: "cOmRider2ActDmgB",  # pc-only
    0x32955436: "cSetInfoOmCrouch",  # pc-only
    0x32955CB4: "D1CRTC_UPDATE_LOCK",
    0x329FE8B5: "cItAction_it_act_throw",  # pc-only
    0x32A66728: "_FILE_INFO_BY_HANDLE_CLASS",
    0x32A70B36: "cEm34ActAbort",  # pc-only
    0x32A85A61: "std::_Unchanged_checked_iterator_base_type_tag",
    0x32A976BE: "PCIE_RX_TLP_HDR1",
    0x32AAE8A8: "AZ0_LOOPBACK_RX_CRC_MASK",
    0x32B0B150: "cEm65ActDash",  # pc-only
    0x32B42695: "rSoundStreamRequest::ReadHeader",
    0x32BBA048: "sPrim::FUNC_PRIM_TONEMAP",
    0x32BBF255: "IOC_BSB_SLV_REQ_CRC_1",
    0x32C215D7: "CAacDecoderDynamicCommonData",
    0x32C23F37: "uPointShadowLight",
    0x32C6A68A: "_DXVA_SliceInfo",
    0x32C701B9: "cEm40ActDmgSmall",  # pc-only
    0x32C9823F: "D1MODE_INT_MASK",
    0x32CA6D86: "CAPTURE_START_STATUS",
    0x32D74A9B: "_DXFILELOADRESOURCE",
    0x32DB54FF: "FSB_LX_PMCTRL",
    0x32DBA3F2: "cEm84ActDmgSpecial",  # pc-only
    0x32DCC873: "REG_MACRO_DATA_1",
    0x32DE3C34: "SQ_CONSTANT_3",
    0x32DF3D8E: "FSB_TLA_PATT_CARE_MASK2",
    0x32E2B7E4: "sPhysics",
    0x32E92BA0: "cFSMOrder::FuncParamPosAngle",  # pc-only
    0x32EB76D8: "uOm08ed_FirePump::cActBase",  # pc-only
    0x32EF3F93: "CContentAndUpdateBase::__vftable",
    0x32F2C485: "XUIInitParams",
    0x32F74720: "NetworkCommunityLive::moveInitNetwork::__l3",
    0x32FAB5DC: "HavokInfo",  # pc-only
    0x32FDB173: "Fex",
    0x33079F9C: "rSoundSpeakerSetXml::MyDTI",
    0x3308C90A: "EFC_PARAM_AXIS_SPD",
    0x330A80D6: "DC_PERFCOUNTER0_SELECT",
    0x330AC40F: "RecordType",
    0x33104CAF: "_XVOICEMAILUI_RESULTS",
    0x33110150: "_D3DXEFFECTDEFAULTTYPE",
    0x3313992E: "_XEXIMAGE_LIBRARY_VERSION",
    0x331619A6: "cEm30ActBuruburu",  # pc-only
    0x3319187C: "XG_MCT::tree_node",
    0x331A1A81: "uEm34::cEm34ActAtkDeath_PL",  # pc-only
    0x33284427: "VC_DEBUG_REG9",
    0x33292905: "RBBM_PERFCOUNTER2_SELECT",
    0x332B4AAB: "sSoundN::MultiBandEQBaseUnit",
    0x332EC504: "ID3DXEffectPool",
    0x33394A8E: "cEm42CActDeadLock",  # pc-only
    0x3339AE35: "DC_PERFCOUNTER0_LOW",
    0x333EDCF0: "RB_AZ0_BC_CRC",
    0x333FD3E9: "_KWAIT_REASON",
    0x3346735F: "BIU_PERFCOUNTER1_LOW",
    0x3346DC68: "tagFrameType_WMV",
    0x3347CB4B: "AZ1_MRU_BANK7_DEPTH_MASK",
    0x33508DAF: "cWpAction_wp0d_act_coop_load",  # pc-only
    0x33519273: "D3D::BufferState",
    0x3356556A: "_XRESOLVE_NAME_RESPONSE",
    0x335A0371: "PCIE_HDR_LOG1",
    0x335C32C3: "sSoundN::VOICE_STATUS",
    0x3361BE11: "CCalMemoryStream",
    0x336BA11D: "PatInterface::LayerPosition",
    0x336CFE99: "DC_TEST_DEBUG_BUS_CLK1_SEL",
    0x336FFA3E: "FpFormatDescriptor",
    0x3372827D: "MtCollada::Skin::MyDTI",
    0x337511EF: "UVBASE_CREATEVOICEMAILPARAM",
    0x3376C4E5: "rMovieOnMemory::MyDTI",
    0x337D08E9: "MC1_PAD_CAL_CNTL",
    0x337DB890: "uOmJeep::cActWepDamageFire",  # pc-only
    0x337FC508: "cPlAction_pl_act_attack_ex",  # pc-only
    0x33801B95: "_D3DSCREENEXTENTSTATS",
    0x33809DF4: "VGT_DEBUG_REG6",
    0x3382A91E: "cAITerrainAnalyzerList",  # pc-only
    0x338998B2: "cEm30PlEvent_NeckBiteFinTH",  # pc-only
    0x338AB7D3: "XGI_READSTRINGS_MSG",
    0x33965536: "_VESA_VTB_EXT",
    0x3398A804: "ID3DXEffectVtbl",
    0x33A102BC: "FSB_TX_PMC1_OR",
    0x33A68BC4: "TP0_CNTL_STATUS",
    0x33A97A0F: "_XMSG_PROPERTY_ATTACHMENT_INTERNAL",
    0x33AAA34E: "cEm84ActStrippedAtk",  # pc-only
    0x33ABAE8D: "rClothXml::Chain::MyDTI",
    0x33AC830D: "pairNode",
    0x33AD48BC: "_XMSG_SUMMARY_REQUEST",
    0x33BB0D05: "Addressing",
    0x33C000E1: "XONLINE_OFFERING_RELATION",
    0x33C2A62B: "NetworkSessionStable",
    0x33C4460C: "cSynchronization::__vftable",
    0x33C46099: "uOm0201_Piano::cActFailed",  # pc-only
    0x33C88475: "ID3DXEffectStateManager",
    0x33CDB4CC: "_XMOUNTUTILITYDRIVEFUNCS",
    0x33D0EFDB: "cEm66ActDmgWater",  # pc-only
    0x33D6C471: "IOC_REG_BUS_CNTL",
    0x33D75751: "_D3DXSHADER_WRITEINFO",
    0x33D77935: "cOmTestAction_om_act_die",  # pc-only
    0x33DB98A0: "uOm095e_Kick::cActPush",  # pc-only
    0x33E1F2E3: "ID3DXEffectCompilerVtbl",
    0x33E24CBC: "VGT_DI_INDEX_SIZE",
    0x33E29E96: "cEm82DmgPinion_PL",  # pc-only
    0x33E38F83: "MC0_INTERRUPT_ACK",
    0x33E4F2FB: "cPlAction_pl_act_coop_jump_broad_6m_first",  # pc-only
    0x33EDFAAD: "_FSCACHE_PROCESS",
    0x33EFFF41: "uModel::RenderInfo::UVOFS",
    0x33F0DF86: "uOm1317_S109_Glass::cActCrash",  # pc-only
    0x33F5CD65: "cPlAction_pl_act_damage_lie_wait_back",  # pc-only
    0x33F79064: "cPlAction_pl_act_damage_sulfate_l",  # pc-only
    0x33F83CB0: "VGT_GROUP_CONV_SEL",
    0x33FAF2EE: "MtSpline",
    0x33FCC149: "PatInterface::Invite",
    0x3403C103: "uEffectVFR::Billboard",
    0x3403F2CB: "_XGMCT_COMPRESSION_PARAMS",
    0x34064933: "cPlAction_pl_act_item_use_partner_second",  # pc-only
    0x3409CE09: "cWpAction_wp_act_wall_stick_t_ready",  # pc-only
    0x340A8002: "uOm08ac_Fence::cActBase",  # pc-only
    0x340C11B7: "LargeValDecodeStatus",
    0x340FF575: "PlusSelection",
    0x3413D3D2: "cEm32ActDieFreeze",  # pc-only
    0x34144B67: "MC0_RD_STR_DLY_1",
    0x3415A58B: "cEm6dActDie",  # pc-only
    0x34180726: "cOmCoopGateAction_om_act_ready",  # pc-only
    0x341A6EB0: "cEm10ActDashCatch",  # pc-only
    0x341B97DB: "_UPDATE_PARENTAL_CONTROLS_STRUCT",
    0x342487B5: "MtGeomCone",
    0x34253632: "cEm80ActInjection_PL",  # pc-only
    0x3426F7BD: "_VESA_COORDINATED_VIDEO_TIMING",
    0x34287C1C: "_QUERY_SELECT_REQUEST",
    0x3428DAD5: "cPlAction_pl_act_walk_r",  # pc-only
    0x342A0C36: "sCamera::Viewport",
    0x342A4763: "ID3DXFileEnumObject::__vftable",
    0x342C34BE: "XNQOSINFO",
    0x342C5F96: "cEm52ActSteerF",  # pc-only
    0x3431BBDC: "cEm30ActNeckBiteHit",  # pc-only
    0x3432827C: "uWater::FILL_TYPE",
    0x343C4197: "GPUSAMPLES",
    0x34428031: "_HSIO_TRAINING_STATUS",
    0x3443C8E3: "MtCollada::Element",
    0x34469C94: "sPrim::DispLevelOrder",
    0x344AFFDE: "_DXVA_VideoProcessCaps",
    0x344D9709: "_UCODE_R500VSUCODE",
    0x34502F0A: "rSoundSource::SAMPLE",
    0x345071A8: "_HAL_POWER_DOWN_REGISTRATION",
    0x345349D9: "IMPORT_OBJECT_HEADER",
    0x3453EE4A: "rEffectSetData::DRAW_OPTION_FLAG",
    0x34560365: "cEm70ActThreat",  # pc-only
    0x3456A8CC: "cPlAction_pl_act_attack_combo_hook",  # pc-only
    0x3457ACE4: "ONSET_Mblk",
    0x345BE9E8: "XECRYPT_AES_STATE",
    0x34636C7E: "cEm0cActWait",  # pc-only
    0x34733DBC: "XNetCapBuffer",
    0x347A3801: "uOmLaserMirror::cActBase",  # pc-only
    0x347DB63A: "t_decoder_context",
    0x34816A78: "MP4MovieFragmentHeaderAtom",
    0x34820BC7: "cPlAction_pl_act_gunemp_ride_off",  # pc-only
    0x348396B5: "_D3DVERTEXBLENDFLAGS",
    0x3485394D: "XAUDIO::CXenonRenderer::__vftable",
    0x348BBF35: "uEffectEdit::Hit",
    0x348F1ECD: "IMPORT_OBJECT_TYPE",
    0x3491F924: "tCMotionVector_X9_EMB",
    0x3493ADF3: "_XGI_STATSENUM_MSG",
    0x34952A27: "constant",
    0x34989B8E: "TPC_CNTL_STATUS",
    0x349B5055: "_XUSER_SIGNIN_STATE",
    0x349D0E3E: "sPrim::Prim::METADATA_HEAD",
    0x34A25F32: "cEm80ActSyutoRevWait_PL",  # pc-only
    0x34A59FB8: "uEffect2D::LifeKeyframe",
    0x34A5FC52: "RTS_EDGE_0_DX",
    0x34A705BD: "sShader::ParameterDesc::MyDTI",
    0x34AD0317: "VC_PERFCOUNTER0_SELECT",
    0x34ADAAE0: "MP4SceneDescriptionMediaHeaderAtom",
    0x34AE6EF2: "cDemoMovie",  # pc-only
    0x34B03A5A: "MachineUniqueId",
    0x34B08A7E: "ScalarOpcode",
    0x34B27600: "_ADD_PAYMENT_INSTRUMENT_REQUEST",
    0x34B81E36: "NetworkRankingLive::moveGetRankingScoreListByFriendList::__l3",
    0x34B8C565: "MOTION_PARAM::TYPE",
    0x34BBA267: "cEm84PlEvent_StripDmg",  # pc-only
    0x34BF7F11: "DQuantDecParam",
    0x34C383B2: "XUIMessageSetBackScene",
    0x34C38669: "_XHTTP_REQUEST_DOWNLOAD_TO_CACHE_RESULTS",
    0x34C4316D: "RIFFHEADER",
    0x34C91626: "cOmCoinActWait",  # pc-only
    0x34CF245B: "PCIE_P_MISC_DEBUG_STATUS",
    0x34D14DF1: "MtGeomOBB",
    0x34D3255D: "uOm1316_BackupHeli::cEvActOptA_Wait",  # pc-only
    0x34E30069: "AZ0_PRIMARY_STATE_DWORD2",
    0x34E5C826: "cEm61Action",  # pc-only
    0x34E6305A: "MC1_STATUS_1",
    0x34EAB6FF: "SQ_CONSTANT_T3",
    0x34ED59ED: "VGT_DEBUG_REG2",
    0x34F28725: "cEm10ActDmgUpper",  # pc-only
    0x34F2EFBB: "cDemoLogoMovie",  # pc-only
    0x34FBDC7F: "FRAME_CALL_CATCH_BLOCK",
    0x34FD81D2: "_XSIGNATURE_CONTENT_TUPLE",
    0x34FE1562: "MtCollada::Library::MyDTI",
    0x34FF0C09: "XMESSAGING_LARGEPROP",
    0x350ADD65: "XUIMessageEnableState",
    0x350AE892: "APPSERVICECONTEXT",
    0x350FB552: "cEm10ActNeckHang",  # pc-only
    0x3511556A: "IDirectXFileDataVtbl",
    0x35124E2E: "cOma016ActCut01",  # pc-only
    0x35133FDC: "_KIPI_COUNTS",
    0x35136D38: "CP_RT14_SIZE",
    0x35158793: "sFps",  # pc-only
    0x3515C617: "XnKeyInfo",
    0x35179A08: "CMediaStreamASFParser::ASF_FILE_PROPERTIES_OBJECT",
    0x351B3444: "XINVITE_INFO_INTERNAL",
    0x351BE4BA: "MtTorus",
    0x351F5752: "PCIE_PERF_COUNT0_MST_R_CLK",
    0x35252CEC: "_XMICO4",
    0x35259DA7: "NetworkLayer::MemberSearchList",
    0x3527E0F8: "PA_SC_LINE_CNTL",
    0x35289CF9: "SQ_CONSTANT_RT_1",
    0x35328887: "MH_PERFMON_PERFCOUNTER2_SELECT",
    0x35393E7B: "uEm45::cActPlActHold2P",  # pc-only
    0x354411FB: "AdhesionElement",  # pc-only
    0x354A33E9: "_FILE_ALLOCATION_INFORMATION",
    0x354CA2EA: "cEm84ActDashEnd",  # pc-only
    0x354F660F: "_BANNER_LIST_RESULT",
    0x3552F162: "XAUDIO::CXMASourceEffect::__vftable",
    0x3553D4AB: "PCIE_ROOT_ERR_CMD",
    0x355C6B3F: "CFHEADER",
    0x355D0C3C: "_KPOWER_MODE",
    0x35602C4F: "CP_RT8_MASK",
    0x35603B63: "PA_SU_PERFCOUNTER0_SELECT",
    0x35618CE6: "sCollision::CONTACT_TYPE",
    0x35678143: "_P_REPLY_BLOCK",
    0x3579FBAC: "CMp3Stream",
    0x357F0382: "cEm22ActAtkRanbu",  # pc-only
    0x358012E8: "rVibration",
    0x3581AE1E: "cFSMOrder::FuncParamApplyFSM",  # pc-only
    0x35826D18: "_P_FRIENDS_ENUM_CREATE_MSG",
    0x358400E7: "cNetEm6c",  # pc-only
    0x358E4F51: "D3D::CMicrocodeBuilder::Microcode::SetVSOutputDeclarationPatchOffsetsContext",
    0x35900C9D: "cEm40ActFarCatch_PL",  # pc-only
    0x35961FE4: "INBUFDATA",
    0x359C35B2: "cEm10ActAtkSpearJump",  # pc-only
    0x359D298D: "IOC_PERFCOUNTER2_SELECT",
    0x359E151A: "cPlAction_pl_act_attack_combo_upper",  # pc-only
    0x359E5622: "cJointExBase",  # pc-only
    0x35A055BC: "tagWMCScriptCommand",
    0x35AB2328: "uPointShadow::MyDTI",
    0x35AC8538: "cEm8ePlEvent",  # pc-only
    0x35AF61B6: "rChain::MyDTI",
    0x35AFF3A3: "rSoundDirectionalSet::NATIVE_FILE_HEADER",
    0x35B10C6A: "REG_MACRO_DATA_5",
    0x35B74FC1: "cOm08beActStatic",  # pc-only
    0x35B8C3B8: "SQ_DEBUG_MISC_0",
    0x35B8DFF1: "_HEAP_STOP_ON_TAG",
    0x35BF58D8: "NetworkSessionManagerPat::SessionList",
    0x35C3BB58: "CP_STQ_AVAIL",
    0x35C3C781: "_IMAGE_SEPARATE_DEBUG_HEADER",
    0x35CDF0AC: "GpuRangeRed",
    0x35D1AAD8: "MP4AudioSampleEntryAtom",
    0x35D83136: "princeton_digital::denormal_traits",
    0x35E0CA8C: "SDSTREM",
    0x35E30DE9: "NetworkConnectionStable::PacketAndVoice",
    0x35E32EF5: "_XMATCH_SESSION_UPDATE_REQUEST",
    0x35F002F9: "rEffectList::EFL_KEYFRAME_FIX_ANGLE_VECTOR",
    0x35F03E85: "GPU_VALUESPACKET",
    0x35F1D2D3: "cPlAction_pl_act_turn_180",  # pc-only
    0x35F314F4: "RB_PERFCOUNTER2_SELECT",
    0x35F35C67: "uEffectEdit::LensFlare",
    0x35F68B4D: "MtHermiteCurve",
    0x35F772BF: "_XEX_CALLCAP_IMPORTS",
    0x35F8A953: "_IMAGE_TLS_DIRECTORY64",
    0x35FA1FF4: "XBDM_FILEEVENT_TYPE",
    0x35FE40D9: "cOmRider2ActDmgF",  # pc-only
    0x3606D1E3: "sVibration::MyDTI",
    0x360916D0: "_XWMDRM_CREATE_CERTIFICATE_REQUEST",
    0x3609DBD2: "_STF_VOLUME_DESCRIPTOR",
    0x360CF4BC: "SCL1_V_COUNTERS",
    0x360D1C15: "D3D::CCommandBuffer",
    0x3611194E: "CRTC1_DEBUG_04",
    0x36159E37: "rEffectSetData::ResourceInfo",
    0x361A8A5A: "rModel::MATERIAL_INFO::ATTR",
    0x361AA2A3: "rEffectList::COLL_FLAG",
    0x361FB672: "uBackLight::MyDTI",
    0x362158C7: "AZ1_RESET_LOOPBACK_TRANSMIT_LFSR",
    0x36249B79: "IProcModeVtbl",
    0x3627B113: "ID3DXLoadUserData::__vftable",
    0x362AA615: "D1CRTC_COUNT_CONTROL",
    0x362B5C7D: "_DXVA_SampleFlags",
    0x3634CE86: "sCollision::cColTree::CollisionCheckFunc",
    0x363712D6: "sCollision::NodeList::SAPSortData",
    0x3639009D: "uOmS104_Driver::cActWait",  # pc-only
    0x363A17F4: "cEm10ActAtkGunAim",  # pc-only
    0x363DCE74: "NetworkLayer::Area",
    0x36406B7B: "rEffectSetData::LIFE_TYPE",
    0x36428B8A: "NetworkSession",
    0x36436ADF: "cOmCoopCardDoorAction",  # pc-only
    0x36441171: "uAdhesion::FUNC_ADHESION_NORMAL_TYPE",
    0x36449D05: "rModel::PRIMITIVE_INFO::CONNECT",
    0x364633CD: "_D3DVECTOR",
    0x36466499: "_XEX_SERVICE_ID_LIST",
    0x36493E32: "rEffectList::EFL_PARAM_COLL",
    0x36495C5F: "uIdItemGet00",  # pc-only
    0x36496385: "ROM_BAD_PIPE_DISABLE_REGISTER",
    0x3649EB1F: "MtColor",
    0x3649EC12: "cLinkUnitObjModel",  # pc-only
    0x364BD7E0: "GPUTEXTURESIZE_3D",
    0x365130C1: "EP_COMMAND",
    0x365149BC: "_Q_ENUM_MESSAGES_MSG",
    0x36531612: "EFC_ANM",
    0x36549AEE: "sGpuParticle::Particle",
    0x3655ED77: "D3D::WorkerState",
    0x36632B09: "MtCollada::Node::TYPE",
    0x366536F7: "XDVO_CRC_MASK_SIG_CNTL",
    0x36671175: "MSI_MSG_DATA",
    0x36679EBC: "GPUREQUESTSIZE",
    0x366A0E85: "std::_Locinfo",
    0x366CC7AD: "cEm44ActWait",  # pc-only
    0x366D58EA: "CCalBufferedFileStream",
    0x3675FCF2: "CP_RT14_COMMAND",
    0x3678388C: "XAUDIO::CDynamicBatchAllocator",
    0x3681271D: "ConstraintJointToJoint",  # pc-only
    0x3682B0D5: "ID3DXConstantTable",
    0x36877DB5: "_D3DXTRANSITION_TYPE",
    0x36888A85: "DC_TEST_DEBUG_EDGE_TRIGGER_MASK",
    0x368B0DD7: "rScheduler::MyDTI",
    0x368F3E47: "__type_info_node",
    0x36909083: "cWpAction_wp0d_act_load_second",  # pc-only
    0x3694A441: "rSoundCurveXml::Element",
    0x369758F5: "_D3DFHZS_FLUSHTYPE",
    0x3699795F: "IXuiTexture",
    0x369AED01: "uOm08e9_S303Elev::cActEnd",  # pc-only
    0x369BAA0C: "CCalMoviePlayer",
    0x369C12D5: "uColorFogFilter",
    0x36A25E7C: "sBioSoundMan",  # pc-only
    0x36AA48EF: "XSTORAGEDEVICECHANGE_PARAMS",
    0x36AB58D2: "XAUDIOVOICEOUTPUT",
    0x36AC26A5: "_XCONFIG_TIMEZONE_DATE",
    0x36B17766: "_XACCOUNT_GET_ANID_REQUEST",
    0x36B25B69: "MtCollada::Skew::MyDTI",
    0x36B515FC: "uEffectVFR::MovePathStrip",
    0x36B6B9EF: "cOmLadderAction_kick",  # pc-only
    0x36BA3096: "XUIMessageGetSetBasePath",
    0x36BE4D50: "uModel::MJOINT_WORK_SAVE",
    0x36C54166: "GPUCmdFrameRenderDone",
    0x36CA3E0B: "NetworkConnection::__vftable",
    0x36D5101A: "IDirectXFile::__vftable",
    0x36D86A5C: "cEm84ActDash",  # pc-only
    0x36DEDC5F: "GPUTRICLAMP",
    0x36E1713F: "CP_RT6_BADR",
    0x36E29465: "rHkCollision",  # pc-only
    0x36E3376B: "rEffectList::EFL_PARTICLE_DRAW_COMMON",
    0x36E4E47F: "cEm10ActAtkBothHand",  # pc-only
    0x36E51DA8: "_UCODE_DEFINITION_TABLE_SIMPLESTATEDELTA",
    0x36E726BB: "_XSIGNATURE_VERIFY_REQUEST",
    0x36EA3144: "ID3DXAnimationControllerVtbl",
    0x36EAD6A9: "_P_PRESENCE_ITEM",
    0x36EC26A5: "XAUDIO::XMAPLAYBACK",
    0x36F0CB3D: "cEm83Action",  # pc-only
    0x36F717CD: "FANIM_PARAM",
    0x36F7C71C: "uOmJeep::cActWepActEv00",  # pc-only
    0x3700E5AA: "PA_CL_ENHANCE",
    0x370119D1: "_XEKEY_INDEX",
    0x37062C9D: "FSB_LX_DDAT3",
    0x3706EC44: "cEm6cActWalk",  # pc-only
    0x370C5480: "PatInterface::FmpInfo",
    0x3711766D: "_FILE_END_OF_FILE_INFORMATION",
    0x3713CA8D: "IDirectXFileEnumObjectVtbl",
    0x37148E8C: "CP_RT15_REFERENCE",
    0x37160A0F: "_FILECACHEITERATORSTATE",
    0x371853C5: "rEffectSetData::INP_TYPE",
    0x371BAA3D: "CXuiScene",
    0x371CFADF: "tagSP_CIRC_BUF",
    0x37235A8D: "_ENUMERATE_TITLES_BY_FILTER_RESPONSE",
    0x37263A51: "uOm1317_Glass::cActCrack",  # pc-only
    0x372781B8: "cEm20ActAtkHangingEscape_PL",  # pc-only
    0x37286F92: "_ADD_PAYMENT_INSTRUMENT_RESPONSE",
    0x3729DD5B: "XTITLE_SERVER_INFO",
    0x372A8A29: "CCalImageRenderer",
    0x372CEB84: "MtThread",
    0x372D2D8E: "MtFloat4A",
    0x37322B5D: "FPARAM_QUATERNION",
    0x3735A84D: "_XSTORAGE_ENUMERATE_PARAMS",
    0x37364B00: "_tagBITMAPFILEHEADER",
    0x373920A9: "sCollision::ScrColInfoPreTraverse",
    0x373BAEA2: "cWpAction_wp0d_act_load_ground_first",  # pc-only
    0x373CB208: "_VOLUME_CONTROL",
    0x374403C4: "RB_DEPTHCONTROL",
    0x3749B45B: "FSB_TR_DEBUG_LO_AND",
    0x374E9A3C: "cEm10ActBackHold",  # pc-only
    0x3751C5BC: "uOmLaserMirror::cActReady",  # pc-only
    0x3753E5DF: "CCalImagePlayer::ImageAnimation",
    0x37593C03: "_XUICLASS",
    0x375BF10B: "_XCONFIG_CATEGORY_TYPES",
    0x3768BCEF: "FSB_TX_PMC5",
    0x376B4C0B: "cNetEm82",  # pc-only
    0x376C2228: "sCollision::NodeList::MyDTI",
    0x376E7F33: "_XACTIVATION_GET_TITLE_LIST_REQUEST",
    0x376EA423: "D1CRTC_PIXEL_DATA_READBACK",
    0x376EE62C: "rShader::MyDTI",
    0x376F8056: "_QUERY_REMOVEID_REQUEST",
    0x377159D1: "MtFileStream::MyDTI",
    0x3772C4B8: "EP_STATUS",
    0x3778C0F7: "_EXCEPTION_DISPOSITION",
    0x377BD4A5: "LOTAreaNo",  # pc-only
    0x377ECED0: "cEm84ActDmgParts",  # pc-only
    0x3781B573: "XGI_READWRITETILE_MSG",
    0x37844CCB: "tagCClipResize",
    0x37857640: "XUIMessageMessageBoxReturn",
    0x378CCA33: "CFFOLDER",
    0x378CF426: "cNetEm65",  # pc-only
    0x378DDD1D: "uOm0201_Piano::cEventActBase",  # pc-only
    0x378E22F0: "uOmExplosive_Fell::cActFallen",  # pc-only
    0x37975DED: "uLight::ATTR",
    0x379AAD64: "D1GRPH_PITCH",
    0x379D9806: "rModel::MyDTI",
    0x379EDB78: "PCIE_PERF_CNTL_MST_C_CLK",
    0x379FE50C: "cTrans",
    0x37A39C92: "uCuboidShadowLight",
    0x37A547B4: "uOmSwitch3::cActMidLoop",  # pc-only
    0x37AAE488: "XVOICE_PACKET_QUEUE",
    0x37B7DCB4: "RB_BC_AZ0_CRC",
    0x37B7E4A1: "PatInterface::UserBinary",
    0x37B98D59: "_DXVA_Frequency",
    0x37BDBCCA: "cEm8cAtkDrillWait",  # pc-only
    0x37C17847: "TCD_DXTC_ARB_DEBUG",
    0x37C178FC: "_D3DPRIVATE_RECT",
    0x37C63EE2: "D1OVL_START",
    0x37C8DADE: "_D3DSHADER_PARAM_SRCMOD_TYPE",
    0x37CD9EC7: "cFlag",  # pc-only
    0x37CF6B9F: "sRender::DISPLAYMODE",
    0x37D110D2: "uDOFFilter::MyDTI",
    0x37D116E6: "GPUBORDERCOLOR",
    0x37D545BF: "_XARB_REPORT_LOST_MACHINES",
    0x37DD5A60: "XAUDIO::XAUDIOCHANNELMAPENTRYEX",
    0x37E13AC4: "NetworkSessionManagerPat",
    0x37EA223E: "CRawDataInfo",
    0x37F5E6E9: "tagWMAFileStatus",
    0x37F6728F: "PIXMeta",
    0x37F730DF: "XAUDIO::XMA_PLAYBACK_LOOP",
    0x37F9DFDD: "TCR_PERFCOUNT_SELECT",
    0x37FADF17: "sLightLinker::ImagePlane",  # pc-only
    0x380D044D: "PIX_REQUEST_SET_OPTIONS",
    0x380E5F46: "sPrim::Prim::VertexFormat",
    0x380F0830: "uOmDive::cActBase",  # pc-only
    0x381413F1: "uChain::CollisionWork",
    0x3816638E: "uModel::Constraint",
    0x381BDFA0: "XUIMessageSuspend",
    0x38238BC0: "EP_SUB_CLASS",
    0x382A5D5E: "sToolBase::SYSMENUINFO",
    0x382B45B7: "SSID_CAP_LIST",
    0x382EA810: "_VERIFY_BILLING_TOKEN_REQUEST",
    0x38305FF7: "_TOKEN_TYPE",
    0x3830D317: "HZ_PERFCOUNTER1_LOW",
    0x383DF9F9: "cPlAction_pl_act_damage_get_up_back",  # pc-only
    0x3847D808: "uActorModel::EffectEmitter",
    0x384A1DCD: "MtCollada::Code::MyDTI",
    0x384B0E26: "cPlAction_pl_act_die_wesker_blow",  # pc-only
    0x384E9AB3: "cOmDoorActOpenKick",  # pc-only
    0x385268BD: "FACIAL_PARAM::TYPE",
    0x3853727B: "charNode",
    0x385C8771: "MP4MemoryInputStreamRecord",
    0x3860F744: "uOm0026::cActMove",  # pc-only
    0x3861202A: "uModel::MJOINT_WORK",
    0x3869037A: "MtPreProcessor::MACROINFO",
    0x387719BB: "PatInterface::Account",
    0x38829EB2: "FSB_LX_LSPARE",
    0x388543C8: "SQ_INSTRUCTION_CF_EXEC_1",
    0x388A8A94: "cTrans::Technique::PS",
    0x388D9237: "cEm10ActBobDown",  # pc-only
    0x389718C2: "uEffectVFR::MovePathKeyframe",
    0x3897890A: "_XMATCH_SEARCH",
    0x3899557F: "_s__CatchableTypeArray",
    0x389AC1E9: "_s_FuncInfo",
    0x389E3987: "uOm1307_Boat::cActWait_Em",  # pc-only
    0x38A3C4C2: "sEffectBase::__vftable",
    0x38AEB534: "EFC_PARAM_U8",
    0x38B494E8: "uOmS204CrouchPoint::cEventActBase",  # pc-only
    0x38B83992: "PCIE_CI_CNTL",
    0x38B9B1FB: "XAUDIO::CEngine::ThreadAssignments",
    0x38BD1096: "CP3_INT_VECTOR",
    0x38C4A9C9: "WRITEBACK_START",
    0x38C4E990: "PA_CL_UCP_1_Z",
    0x38C51F34: "HZ_PERFCOUNTER0_HI",
    0x38C7E539: "rChain::JointInfo::JOINT_ATTRIBUTE",
    0x38C80102: "ID12_OVL_DATA_A",
    0x38D04A8C: "MtCollada::Accessor::MyDTI",
    0x38D31F52: "NetworkLayer::MemberNumReceive",
    0x38D7FEFC: "cPlAction_pl_act_weapon_ready_end",  # pc-only
    0x38DAF317: "NB_MMR_BAR",
    0x38DBE10E: "t_ContextWMV",
    0x38E2EF3F: "uOmS705ceil::cActLand",  # pc-only
    0x38E41678: "CARDEA_CSP_INTERFACE_IMP",
    0x38E9F5A5: "_FILE_RENAME_INFORMATION",
    0x38F2E016: "_XFRIENDS_REQUEST_PARAMS",
    0x38F34138: "_D3DLIGHT9",
    0x39063C99: "PREF_LIMIT_UPPER",
    0x390683A7: "PA_CL_UCP_0_Z",
    0x39075D6C: "IPersist",
    0x39099F44: "_XCONFIG_SYSTEM_ENTRIES",
    0x390EF6D0: "cEm8cAtkGroundHitStart",  # pc-only
    0x391124E7: "_D3DXEFFECT_DESC",
    0x39125955: "cPlAction_pl_act_gunemp_ready_loop",  # pc-only
    0x3912A61C: "AZ0_LOOPBACK_PATTERN1PHS1",
    0x3914F518: "uMovie::Player::FrameData",
    0x39150136: "rEffectList::EFL_PARTICLE_LIGHT",
    0x3915AAB7: "MtStream::__vftable",
    0x39196F4D: "MtFCurve",
    0x391A774B: "CP_RT6_COMMAND",
    0x391C10E1: "VGT_DI_PRIM_TYPE",
    0x392D4EA2: "D3D::SetEncodedThreadId",
    0x39313102: "SX_PERFCOUNTER0_LOW",
    0x3935DB8B: "AZ1_COPY_STATE_DWORD0",
    0x39384861: "sShader::FUNC_SHADOW_MAP_TYPE",
    0x39398346: "sVibration::FADE_TYPE",
    0x393FAE6A: "_XMFLOAT4X4",
    0x39404C8F: "rNavigationMesh::nodeData",  # pc-only
    0x39459660: "NetworkSessionManagerLive::QOS_FOR_SESSION",
    0x3947BA00: "PA_SC_PERFCOUNTER0_LOW",
    0x394BA276: "uMotionCamera::MyDTI",
    0x394F4B33: "tagWMCContentDescription",
    0x3957ABFF: "SETUP_DEBUG_REG5",
    0x395998D8: "cOmJeepAction_om_act_result",  # pc-only
    0x3959A333: "std::basic_streambuf",
    0x395F343E: "_GET_ACCOUNT_INFO_FROM_PASSPORT_REQUEST",
    0x3963E984: "PatInterface::MailId",
    0x39670AE0: "SCRATCH_CMP_CNTL",
    0x39672C1B: "cEm10ActSitStand",  # pc-only
    0x396761E8: "sCollision::ScrColInfoGetAreaPoly",
    0x3967E8E4: "CLVOICE",
    0x3968CF8B: "_XMHENDN3",
    0x396AA87C: "RTS_Z_DX_MSBS",
    0x396D3A08: "rShader::TECHNIQUE_INFO",
    0x396DC092: "NetworkCommunityLive::moveGetFriendList::__l3",
    0x396F46E7: "cEm41CoreAction",  # pc-only
    0x39714801: "cAIDynamicPathFinding::TraceManagement",  # pc-only
    0x3975F45D: "cPlAction_pl_act_damage_syokei_lie",  # pc-only
    0x397DDE97: "_TOKEN_USER",
    0x39813CE9: "FSB_TLA_CONDITION2",
    0x3987D63B: "BIU_INT_BAD_REG_ADDR",
    0x3989D10F: "_FILE_ALIGNMENT_INFORMATION",
    0x398AED0D: "transitiondate",
    0x398FE86A: "cOmJeepAction_om_act_forward",  # pc-only
    0x3995CDEC: "_DXVA_BufferDescription",
    0x39967E9C: "cAIFSM::Action",  # pc-only
    0x399BE2D5: "cFSMOrderPlayer::FuncParamOrderFSM",  # pc-only
    0x399EB38A: "rEffectList::RANGE_OPTION_FLAG",
    0x39A38612: "MtCollada::BoundingBox",
    0x39ACDBBE: "rEffect2D::UNIT_OPTION_FLAG",
    0x39B5137B: "_XBMOVIE_CAPTURE_FILE_HEADER",
    0x39BEE871: "cWpAction_wp_act_fire",  # pc-only
    0x39C13343: "rEffectList::EFL_PARTICLE_LINE",
    0x39C52040: "rCameraList",
    0x39C73911: "rSoundSourceSEInterMediate",
    0x39C8FD0E: "uOmS204CrouchPoint::cActCrouch",  # pc-only
    0x39CB9370: "rEffectSetData::ESD_MOVE_MUL",
    0x39CF3C39: "MC1_RD_BUFFER_CNTL_0",
    0x39D3ACDA: "CP_RT_STAT",
    0x39D54997: "MtCollada::Source",
    0x39D8A435: "rEffectSetDataList::DIRECITON_TYPE",
    0x39DB5976: "XHVBATCHALLOCATOR",
    0x39DF6DC1: "XAUDIO::CSourceEffect::__vftable",
    0x39E5E5C2: "SCHEMA_DESCRIPTOR",
    0x39E6C9AF: "uEffect2D::GEN_STATUS",
    0x39E81842: "IOC_PERFCOUNTER1_HI",
    0x39E87A19: "_IMAGE_OS2_HEADER",
    0x39EEF98F: "std::_String_val",
    0x39F12FBB: "sMain",
    0x39F7917A: "CP_RT6_REFERENCE",
    0x39F98525: "cEm10ActDmgFall_F",  # pc-only
    0x3A041F3F: "CombFuncX",
    0x3A086CB1: "FSB_LX_LERSTM",
    0x3A092DA3: "RBBM_WAIT_IDLE_CLOCKS",
    0x3A0B3E9D: "_Q_REVOKE_MESSAGE_MSG",
    0x3A0C37A6: "cEm70ActErase",  # pc-only
    0x3A12139C: "uOmCoopJumpBroad::cActPlBase",  # pc-only
    0x3A129ADD: "uEffect2D::PTCL_STATUS",
    0x3A135CCE: "cTrans::RT_FLAGS",
    0x3A13B33B: "cEm10ActAtkGunPeepL",  # pc-only
    0x3A170407: "_D3DRASTER_STATUS",
    0x3A196F27: "PIX_FRAME_SWAP",
    0x3A1D81D9: "MtProfiler",
    0x3A1DA8C3: "cSystem::__vftable",
    0x3A217B78: "MtCollada::Scale",
    0x3A21D417: "cScenarioParam",  # pc-only
    0x3A2204F4: "VC_PERFCOUNTER3_SELECT",
    0x3A25661B: "_OSVERSIONINFOW",
    0x3A28303F: "GPUVERTEXSIGN",
    0x3A2A6755: "CHUDSceneImpl",
    0x3A3AC2EF: "MP4ObjectDescriptorAtom",
    0x3A3FD419: "cPlAction_pl_act_knife_ready_loop",  # pc-only
    0x3A4332A8: "MtCollisionEpa::MyDTI",
    0x3A48576C: "FSB_TX_CMDMM0",
    0x3A4A0380: "cOmBoatAirAction_pl_act_change_ready",  # pc-only
    0x3A4BBF18: "uSpotLight::MyDTI",
    0x3A56E36C: "_IMAGE_IMPORT_DESCRIPTOR",
    0x3A58F75C: "COHER_DEST_BASE_4",
    0x3A5F0D36: "cAnimRect",  # pc-only
    0x3A6240E2: "cPlAction_pl_act_attack_knife_licker_tongue",  # pc-only
    0x3A64FF31: "XDVO_DEBUG3",
    0x3A6C9E2B: "_BASIC_CONTENT_INFO",
    0x3A6CC619: "CameraSequenceInfo",  # pc-only
    0x3A70A3AB: "CVector",
    0x3A77649A: "cEm10ActAtkGunWarnShotL",  # pc-only
    0x3A7CF6DD: "EFC_KEYFRAME_VECTOR",
    0x3A8257C9: "PA_CL_UCP_2_Z",
    0x3A82790E: "cUnit",
    0x3A884521: "_EDID_BLOCK_MAP",
    0x3A8BCFAE: "XUINotifyHtmlLinkActivated",
    0x3A9043B2: "CBitSequence::__vftable",
    0x3A915393: "rArchive::MyDTI",
    0x3A918992: "tTask_MT",
    0x3A91F4EC: "cNetEm30",  # pc-only
    0x3A945D1B: "DQuantDecParam_vector4",
    0x3A9607E4: "_REMEMBEREDFILE",
    0x3A962172: "rSoundDirectionalCurveXml::Element",
    0x3A96B54F: "std::bidirectional_iterator_tag",
    0x3A96D8A0: "rSoundDirectionalCurveXml",
    0x3A97647E: "rSoundStreamRequestXml::ElementData::MyDTI",
    0x3A99C1F9: "XDVO_CRC_SIG_CNTL",
    0x3A9B7358: "uLightScatteringFilter",
    0x3A9E080C: "VC_DEBUG_REG5",
    0x3A9F495A: "XUI_CONTENT_TYPE",
    0x3A9F9545: "MtCollada::Mesh",
    0x3AA02C23: "ID3DXAnimationCallbackHandler",
    0x3AA381DA: "_XCONFIG_CONSOLE_ENTRIES",
    0x3AA4B35E: "XAUDIO::CCriticalSection::__vftable",
    0x3AA9A342: "rSoundRequest::SOUND_REQUEST_COMMAND",
    0x3AAA29FF: "_XCONFIG_STATISTIC_SETTINGS",
    0x3AAB8926: "PCIE_ERR_CNTL",
    0x3AACDDF1: "_XMSG_PROPERTY",
    0x3AC23513: "AZ1_PRIMARY_STATE_DWORD1",
    0x3AC79440: "DMIF_DEBUG02",
    0x3AC7C6F1: "_FILE_FS_DEVICE_INFORMATION",
    0x3AC94102: "uOm1316_BackupHeli2::cActAppear",  # pc-only
    0x3ACBB68A: "cOmBreakAction_break",  # pc-only
    0x3ACBC1D9: "rEffectList::EFL_MOVE_COMMON",
    0x3AD0F2E9: "sVibration::PadVibration",
    0x3AD17542: "tagWMA_PayloadExtensionSystem",
    0x3AD355FF: "rSoundSpeakerSetXml::DirectionalCurveElement",
    0x3AD48D75: "XPLAYERLIST_FLAGS",
    0x3AD8C229: "sPrim::FUNC_PRIM_NORMALMAP",
    0x3AD8D468: "ID3DXAnimationSetVtbl",
    0x3ADB440C: "SQ_CONTEXT_MISC",
    0x3ADC638D: "cEm41CActDiscloseLoop",  # pc-only
    0x3AE131F6: "CP_RB_WPTR",
    0x3AE251F2: "tagAudioType_WMC",
    0x3AE7485B: "UVBASE_ENUMERATEVOICECHATSPARAM",
    0x3AEDF63F: "_XMEDIA_PLAYBACK_STATUS",
    0x3AEE4556: "_XPROFILE_GAMER_TYPE_VALUES",
    0x3AF0BBE4: "ID3DXSpriteVtbl",
    0x3AFBA91C: "RTS_J_W_REF",
    0x3AFBFEBB: "cEm80ActSyutoEsc_PL",  # pc-only
    0x3AFD5CC3: "sVibration::VIB_REQ_TYPE",
    0x3AFE9197: "NetworkSessionManagerPat::SessionInfo",
    0x3B0037E7: "AZ0_ACC_MASK",
    0x3B04194B: "_XGI_CREATEENUM_MSG",
    0x3B113DEB: "rSoundSourceXMA::XMASTREAMFORMAT",
    0x3B122E6E: "IOC_PERFCOUNTER1_SELECT",
    0x3B17F982: "__lc_time_data",
    0x3B187B90: "cEm45ActPillar",  # pc-only
    0x3B199F3A: "_XOFFERING_CONTENTAVAILABLE_RESULT",
    0x3B19B497: "cEm30ActSniffBgn",  # pc-only
    0x3B1A4D72: "PIX_INDEX_VIDEO",
    0x3B1BC833: "ID3DXCompressedAnimationSetVtbl",
    0x3B2EC248: "cOmLockAction",  # pc-only
    0x3B33A5AB: "cResource::NATIVE_TYPE",
    0x3B342ADD: "IPersistStreamVtbl",
    0x3B34CABE: "uOmJeep::cActWepActResult",  # pc-only
    0x3B38779F: "_XNPLISTCHANGES",
    0x3B393B8E: "BSB_WRAPPER_PRBS23_ERRCNT0",
    0x3B403DFE: "PA_CL_UCP_3_Z",
    0x3B4342EA: "NetworkPort",
    0x3B465CB8: "CHAINACTION",
    0x3B48E8E4: "_DVD_XGD2_DRIVE_AUTH_RESULT",
    0x3B490DC3: "ROM_PAR_ADDR_REG",
    0x3B496A8D: "sResource::DECODEWORK",
    0x3B4A1C94: "uOm021c_Switch::cActSwitch",  # pc-only
    0x3B4B440B: "_LSP_ENUMERATE_SERVER_INFO",
    0x3B4F5D00: "PCIE_P_CNTL",
    0x3B50CB26: "_IMAGE_BOUND_IMPORT_DESCRIPTOR",
    0x3B50FFE8: "PA_CL_VPORT_YOFFSET",
    0x3B51C496: "CXLiveMuteList",
    0x3B526626: "IOC_BSB_SLV_CPL_CRC_1",
    0x3B553B6E: "uOm0201_Piano::cActBase",  # pc-only
    0x3B59AB6A: "uHSVFilter",
    0x3B5C1E36: "sShader::PARAM_TYPE",
    0x3B5C72E9: "_P_TEAM_LIST_TEAMS_MSG_XUID",
    0x3B5C843B: "cPlAction_pl_act_coop_jump_broad_6m_second",  # pc-only
    0x3B5FD082: "_D3DTAG",
    0x3B636FA6: "MtFloat4x3",
    0x3B65E2B8: "uOm0912_s119Tram::cActPlBase",  # pc-only
    0x3B67597F: "D1CRTC_H_SYNC_A",
    0x3B681D72: "AZ1_LOOPBACK_PATTERN1PHS2",
    0x3B6CB67C: "_DVD_AP25_CHALLENGE_ENTRY",
    0x3B6D00BE: "uEffectVFR::MoveCommon",
    0x3B7125A5: "rSoundCurveSetXml",
    0x3B793AE7: "cEm32TongueActAttack",  # pc-only
    0x3B7A5274: "CCalVideoMetadata::__vftable",
    0x3B7C1317: "RB_PERFCOUNTER1_SELECT",
    0x3B7FD107: "cEmc3ActDownEnd",  # pc-only
    0x3B826C5B: "cOmCoopDoorActionPl",  # pc-only
    0x3B8B00E2: "CXuiControl",
    0x3B8B2623: "CCalEncoder::__vftable",
    0x3B8B84CC: "cEm10ActDeadPlagaB",  # pc-only
    0x3B99A2A9: "MtEllipsoid",
    0x3BA38FAD: "XUIElementPropDef",
    0x3BAA9906: "rEffectList::EFL_PARAM_LINE_LENGTH",
    0x3BABCFE0: "rModel::PRIMITIVE_INFO::LOD",
    0x3BAD4CCD: "cPlAction_pl_act_dummy",  # pc-only
    0x3BB5CBDF: "ID3DXCompressedAnimationSet::__vftable",
    0x3BBB734E: "MtXmlReader::WORK",
    0x3BBB9D55: "SB_BIST",
    0x3BBC0DF5: "_XPROFILE_SYNC_TITLES_RESULT",
    0x3BBD8F64: "MH_PERFMON_PERFCOUNTER1_SELECT",
    0x3BC33274: "uOma004_Collapse::cActSuccess",  # pc-only
    0x3BC43B3F: "ID3DXLineVtbl",
    0x3BC93640: "XAUDIO::_XMA_REGISTERS",
    0x3BCAB639: "cEm84ActReadyEnd",  # pc-only
    0x3BCAFFB5: "rCameraList::MyDTI",
    0x3BCF2401: "IOC_PERFMON_CNTL",
    0x3BCF73A9: "uOm0927_Crane::cActMoveBA",  # pc-only
    0x3BD5D242: "MP4MovieExtendsAtom",
    0x3BD8A288: "SQ_CF_RT_BOOLEANS",
    0x3BDD5531: "XUIMessageGetBackScene",
    0x3BEA805D: "XAUDIOVOICEOUTPUTENTRY",
    0x3BEC4749: "aS109::cActJeepEv01",  # pc-only
    0x3BEC488C: "PCIE_RX_CREDITS_ALLOCATED_D",
    0x3BEE63BB: "NetworkStorageLive",
    0x3BEF3C80: "PA_SU_PERFCOUNTER3_SELECT",
    0x3BF27A8F: "SQ_PERFCOUNTER2_LOW",
    0x3BF33874: "uOmSwitchPulley::cActPulleyGo",  # pc-only
    0x3BF4BA00: "MH_PERFMON_PERFCOUNTER2_HI",
    0x3BF51F9A: "XAUDIO::XMA_PLAYBACK_POSITION",
    0x3BFB0DA7: "cOmJeepAction_om_act_damage",  # pc-only
    0x3C0C71B5: "DNameStatusNode",
    0x3C0CA86C: "sKeyboard::TYPE",
    0x3C14AD49: "uTVNoiseFilter",
    0x3C18CE07: "PCIE_PERF_CNTL_SLV_R_CLK",
    0x3C1B319C: "princeton_digital::allpass2_t",
    0x3C1CB8B3: "CopySrcSelect",
    0x3C26993B: "_FILE_FS_FULL_SIZE_INFORMATION",
    0x3C26F724: "MtGeomSphere::MyDTI",
    0x3C2C57CA: "cLinkUnitParent",  # pc-only
    0x3C3703A9: "IOC_PERFCOUNTER1_LOW",
    0x3C405C02: "_XSTORAGE_BUILD_SERVER_PATH",
    0x3C41B241: "sResource::TypeInfo::MyDTI",
    0x3C46F391: "CXStorageMiscWorker::RESOLVE_NAME_RESPONSE_BUFFER",
    0x3C48F2D5: "URL_COMPONENTS",
    0x3C52353A: "CCalTextureRenderer",
    0x3C54F223: "SB_CACHE_LINE",
    0x3C59175E: "uOm1317_S109_Glass::cActBase",  # pc-only
    0x3C5E64B6: "rSoundPackageXml::ProgramData::MyDTI",
    0x3C603F04: "uBioActorModel",  # pc-only
    0x3C675175: "TEST_CHANGEXEXINFO_MSG",
    0x3C69242B: "_CDROM_SUB_Q_DATA_FORMAT",
    0x3C6A2BD5: "cEm8cAtkArmDancing",  # pc-only
    0x3C6A330A: "MC1_SECURE_MEMORY_APERTURE_LOG_MH",
    0x3C6A5954: "D3D::CXpsThread",
    0x3C6ABF2F: "_REMOVE_PAYMENT_INSTRUMENT_REQUEST",
    0x3C6FFB68: "_XSTAT_PROC",
    0x3C70E33D: "_XINPUT_GAMEPAD",
    0x3C715B09: "_MESSAGEBOX_RESULT",
    0x3C72F7BD: "_XCTDFILE_COMPRESSION_STATE",
    0x3C72FA8F: "cEm8cAtkDrillCatch",  # pc-only
    0x3C7A350B: "GPUMINMAGFILTER",
    0x3C7CAFD8: "CMBColorControl::__vftable",
    0x3C7E4367: "BIOS_6_SCRATCH",
    0x3C8354E1: "VC_type",
    0x3C887B35: "_PASSPORT_GET_BUDDY_GAMERTAG_REQUEST",
    0x3C8A6C4F: "ID3DXConstantTableVtbl",
    0x3C8C4B35: "uOm1307_Boat::cActWait_Start",  # pc-only
    0x3C8DB858: "uFilter::transImageEx::__l2::SCREEN_VERTEX",
    0x3C8F60F2: "cFSMOrderPawn::FuncParamObjAdj",  # pc-only
    0x3C91EAC9: "NCI_CODEC_IO_BLOCK",
    0x3C9268CB: "NetworkSessionManagerLive::MemberInfo",
    0x3C97A4DF: "SQ_INSTRUCTION_CF_LOOP_1",
    0x3CA189BA: "PCIE_LC_STATE3",
    0x3CA2E793: "FSB_LR_DEBUG_LO_AND",
    0x3CA9CEB4: "cEm43ActWait",  # pc-only
    0x3CAC35C7: "uMotionCameraNoise::Noise",  # pc-only
    0x3CB5B341: "cAITreeBase",  # pc-only
    0x3CB8372A: "uHazeFilter::MyDTI",
    0x3CBAE451: "MtDebug",
    0x3CBAF8AA: "cFSMOrder::FuncParamAddItem",  # pc-only
    0x3CBC7A94: "_CSTRING",
    0x3CC395EB: "FSB_TX_PMC5_OR",
    0x3CC47CA0: "sCollision::ScrColInfoFind::MyDTI",
    0x3CCCD89B: "AZ0_MRU_BANK2_DEPTH_MASK",
    0x3CCE58BD: "CCalSubDecoder",
    0x3CD08F16: "cEmc0ActAppear",  # pc-only
    0x3CD27E30: "PA_SC_DEBUG_PKR_0",
    0x3CD3B6B7: "tAsfXAcmAudioErrorMaskingData",
    0x3CD9315B: "XVOICE_EXTENSION",
    0x3CDAAB1C: "cEm84ActDieNormal",  # pc-only
    0x3CDD7428: "_XUIDWITHFLAGS",
    0x3CDE47EA: "CP_ME_VS_FETCH_DONE_DATA",
    0x3CEB1056: "cEm44ActRun",  # pc-only
    0x3CEE40AC: "uRefWater::VERTEX",
    0x3CEF233B: "_FILE_LINK_INFORMATION",
    0x3CF07762: "cEm32ActDie",  # pc-only
    0x3CF83444: "_D3DConstants",
    0x3CF8BFA5: "MP4ListItem",
    0x3CF9968F: "uShadow::VSM_BLUR_TYPE",
    0x3CFA4D5D: "uUniformShadow::MyDTI",
    0x3CFE85EB: "_IMAGE_SYMBOL",
    0x3D0AC74F: "PatInterface::AddressInfo",
    0x3D0BEF1A: "uBioActorPawn",  # pc-only
    0x3D0C2996: "uEffectVFR::PTCL_MOVE_RNO_TBL",
    0x3D0E6964: "BIU_INT_ACK",
    0x3D102967: "_POOL_TYPE",
    0x3D1AF6F1: "ID3DXKeyframedAnimationSet",
    0x3D207318: "uEffectEdit::PolylineKeyframe",
    0x3D23A395: "rSoundEngine::EnginePointData",  # pc-only
    0x3D23C637: "cEm34ActFinalEnd",  # pc-only
    0x3D2DA3A1: "EFC_AXIS_TYPE",
    0x3D353345: "COHER_DEST_BASE_0",
    0x3D3576D6: "XUIGradientStop",
    0x3D3AE57F: "uOm08b8_Limited::cActWait",  # pc-only
    0x3D3B1B36: "NB_REGPROG_INF",
    0x3D3D2C2E: "_XNPARPENTRY",
    0x3D3D7F2C: "FSB_LX_LERST",
    0x3D3DFDF1: "uEffectGenerator",
    0x3D443AF2: "XSVRTCACHE",
    0x3D493383: "_D3DXSHADER_VARIABLEINFO",
    0x3D4B9972: "rPath::PathJoint",  # pc-only
    0x3D4BD7F0: "rChainCol::ColInfo::COLLISION_SHAPE",
    0x3D4D6C2A: "XUIHtmlScrollInfo",
    0x3D525817: "cEm6cActDieIce",  # pc-only
    0x3D568D05: "MtGeomCapsule",
    0x3D57C1B3: "std::_Locbase",
    0x3D59487B: "MC1_CRC_CNTL",
    0x3D5A8100: "TCB_FETCH_GEN_PIPE0_DEBUG",
    0x3D5AC137: "_Huffman_WMV",
    0x3D62893E: "rGridEnvLight::SHFactor",
    0x3D62C7FC: "rModel::ENVELOPE_INFO",
    0x3D63382C: "cOmCoopTwistActRotate",  # pc-only
    0x3D63F509: "COMMANDENTRY",
    0x3D6A56EF: "cLinkUnitOne",  # pc-only
    0x3D6C28DF: "TCD_DEGAMMA_DEBUG",
    0x3D6E4849: "tagWMA_MetaDataDescRecords",
    0x3D7114C9: "cEm10ActAtkBow",  # pc-only
    0x3D77CD3F: "rEffectSetData::RELEASE_TYPE",
    0x3D7D020B: "MtCollada::Light",
    0x3D8134FF: "IXMediaJpegDecoder",
    0x3D874FC6: "_CEA861_SPD_INFOFRAME",
    0x3D879489: "cPlAction_pl_act_damage_knock_down_2",  # pc-only
    0x3D8A41AE: "REG_MACRO_CONTROL",
    0x3D8BDB9A: "CChannelGroupInfo",
    0x3D9243C7: "GPUPERFEVENT_TCM",
    0x3D9595B6: "_STFC_VOLUME_EXTENSION",
    0x3D96F777: "_XPNGENCODE_PARAMS",
    0x3D9C4B1E: "uActorModel::Constraint",
    0x3D9D07E8: "GPUPERFREGISTER",
    0x3D9E9900: "SUB_CLASS",
    0x3DA2BB27: "_HEAP_UNCOMMMTTED_RANGE",
    0x3DA36DC1: "MP4GenericSampleEntryAtom",
    0x3DA62EE6: "RBBM_PERFCOUNTER1_SELECT",
    0x3DA8158F: "FSB_TR_CTRL",
    0x3DAB7875: "PCIE_FC_CPL",
    0x3DAE6377: "ID3DXBaseMesh::__vftable",
    0x3DB2605B: "NB_BIST",
    0x3DB7DA0D: "CXuiSceneCache",
    0x3DBB86E1: "XPLAYERLIST_USER",
    0x3DBC8A62: "CP_RT14_MASK",
    0x3DBF1348: "AHShapeCone",  # pc-only
    0x3DC50306: "uOmSwitch3::cActPushRelease",  # pc-only
    0x3DCD7BFC: "CODEC_PROCESSOR",
    0x3DCDAA61: "D3D::CMicrocodeBuilder::StreamWriter",
    0x3DCFCB15: "CP_RT8_SIZE",
    0x3DD1A7E8: "NetworkLayerPat::LayerInfo",
    0x3DD363E4: "_CRYPTOAPI_BLOB",
    0x3DD91551: "IOC_INT_STATUS",
    0x3DE4304B: "cFSMOrder::FuncParamMessageClr",  # pc-only
    0x3DE4BC88: "_PIXTHREADCAPTUREINFO",
    0x3DE9EE6F: "_P_DEAD_USER_MSG_INTERNAL",
    0x3DEE771D: "XONLINE_PASSPORT_LOGIN_EX_SERVICES",
    0x3DEEB657: "sRender::SAMPLER_TYPE",
    0x3DF05777: "FSB_TR_DEBUG_AUX_AND",
    0x3DF3CC15: "VC_DEBUG_REG1",
    0x3DF6FF56: "HSIO_PHASE_SELECT",
    0x3DFA96BF: "LIST_ENTRY32",
    0x3DFC30F5: "cNetEm34",  # pc-only
    0x3E00A19B: "cEm32ActWalkBgn",  # pc-only
    0x3E03D251: "cEm84ActSitOnHandrailEx",  # pc-only
    0x3E0AB24A: "rEffectList::VIB_OPTION_FLAG",
    0x3E0CB92B: "uDirectionalGlowFilter",
    0x3E0D570C: "cEm84CoreActWait",  # pc-only
    0x3E0EB85B: "uOmUseItem::cActPlMotion",  # pc-only
    0x3E0F2B7B: "PA_CL_UCP_4_Z",
    0x3E11C407: "CP_DEBUG",
    0x3E11FA6D: "GPUPERFEVENT_VGT",
    0x3E137B5B: "CPnsData",
    0x3E1ED081: "DEVICE_STATUS",
    0x3E1F7730: "sLight::BOUNDERY_TYPE",
    0x3E1F7CEC: "cEm4502Action",  # pc-only
    0x3E251F4A: "PA_SC_SCREEN_SCISSOR_BR",
    0x3E2A6FC1: "_heapinfo",
    0x3E2C67E9: "rGridEnvLight::MyDTI",
    0x3E2C7923: "MtFloat3x3",
    0x3E3066C0: "D3D::CDevice::AsyncResourcesData",
    0x3E3154C3: "cWpAction",  # pc-only
    0x3E363245: "rChain",
    0x3E395078: "NetworkLayer::DeliveryList",
    0x3E3A6FE6: "SETUP_DEBUG_REG1",
    0x3E3BDFAE: "FSB_INT_VECTOR",
    0x3E3E1CA1: "sCollision",
    0x3E3F2FBC: "uOm08b3_S203Elev::cActRise",  # pc-only
    0x3E445DCB: "DCP_DEBUG",
    0x3E477C5F: "_D3DSURFACES",
    0x3E4D989D: "MtCollisionGjk::Result::__vftable",
    0x3E4E9BB1: "rSoundPackageXml::MyDTI",
    0x3E54CF51: "tagPALETTEENTRY",
    0x3E55140E: "NetworkBuffer",
    0x3E56B7D0: "MP4Atom",
    0x3E5E118F: "MtCollisionTree::__vftable",
    0x3E5EB13E: "_XEX_FILE_DATA_DESCRIPTOR",
    0x3E64C9A9: "_DXVA_COPPStatusOutput",
    0x3E671B6D: "HSIO_DLL_ADJ3",
    0x3E73F163: "_PASSPORT_LOGIN_REQUEST",
    0x3E7471C5: "IOC_INVALID_AP_COMMON",
    0x3E759F98: "uBioActorPL00",  # pc-only
    0x3E7BB43F: "cOm08beActDynamic",  # pc-only
    0x3E7D30FB: "MtCollada::Technique::MyDTI",
    0x3E7E941A: "cAIWorldInterfaceInputModule",  # pc-only
    0x3E81DBB4: "aS705::Motion",  # pc-only
    0x3E8412A7: "_XPRESENCE_SEND_DEAD_USER",
    0x3E87A22A: "rSoundRandomXml",
    0x3E87ABF2: "cEm40ActFloat",  # pc-only
    0x3E87C1A9: "tagWMVDecMT",
    0x3E883B2E: "cPlAction_pl_act_die_plaga_beat",  # pc-only
    0x3E892835: "FSB_LX_PMC5_AND",
    0x3E94413C: "cEm10ActDmgFall_B",  # pc-only
    0x3E946DE2: "NetworkLayer::Parent",
    0x3E956D14: "PCIE_BUS_CNTL",
    0x3E99E2CC: "GFX_COPY_STATE",
    0x3E9C5AE6: "AACAudioDecoder",
    0x3E9CD7C7: "cEm32ActCeilToGround",  # pc-only
    0x3E9D9027: "STREAMDATA",
    0x3E9F9EDF: "MC1_TIMING_CNTL_1",
    0x3EA35F43: "MtProperty::Custom::PARAM",
    0x3EA784A2: "uOm0944::cActSwitchOn",  # pc-only
    0x3EA7B6E2: "XUIMessageCaretPosition",
    0x3EAF7FE0: "CMpegBitStream",
    0x3EB07876: "sResource::TypeInfo",
    0x3EB09C99: "_XMSG_INVITE_SEND_MESSAGE_PARAMS",
    0x3EB1743F: "_XCONTENT_METADATA_INSTALLER_SYSTEM_UPDATE",
    0x3EB3AF00: "MtCollada::COLLADA::MyDTI",
    0x3EB43982: "_XMARKETPLACE_CONTENTOFFER_INFO",
    0x3EB78AAE: "_CONSUME_ASSETS_REQUEST",
    0x3EB8C8B4: "CP_RT13_POLL_ADDRESS",
    0x3EBA0156: "_D3DINDEXBUFFER_DESC",
    0x3EBC20A5: "PERSTREAMBASE",
    0x3EBC24AD: "cEmc3Action",  # pc-only
    0x3EC06C23: "uRadialBlurFilter::MODE",
    0x3EC09201: "CXContentDownload::REFRESH_LICENSE_RESPONSE_BUFFER",
    0x3EC8931C: "BIU_INT_CONTROL",
    0x3ECC57A5: "MtGeometry::MyDTI",
    0x3ECDE6D8: "uOma00c_UroAction::cActWait",  # pc-only
    0x3ED0D980: "cOmJeepAction_om_act_truck_damage",  # pc-only
    0x3ED17C4F: "MH_INT_CLEAR",
    0x3ED23928: "tagWMVHRD",
    0x3EE0E424: "_LICENSEE_BITS",
    0x3EE24ADD: "_HVSTATS_TLB",
    0x3EE2A0C4: "NetworkSessionManagerBroadcast::BroadcastUniqueId",
    0x3EE794BE: "XUIMessageChildSaving",
    0x3EEA53D7: "cEm30ActDmgYoroke",  # pc-only
    0x3EF60D8D: "RB_COLOR_CLEAR_LO",
    0x3EF83895: "sSoundN::StreamThread",
    0x3EFE0EC8: "_FPIEEE_ROUNDING_MODE",
    0x3EFF601F: "_STACK_FRAME_HEADER",
    0x3F08AB71: "sShader::MOTIONBLUR_TYPE",
    0x3F0A068D: "cPlAction_pl_act_coop_climb_cliff",  # pc-only
    0x3F0A8CBF: "rChainCol::ColInfo::COLLISION_ATTRIBUTE",
    0x3F0BB90D: "INPUTSRCGETDATASTATE",
    0x3F0F057E: "_XPRESENCE_ALIVE_REPLY",
    0x3F10F91D: "tagWMCMetaDataDescRecords",
    0x3F12E521: "sExceptionHandler",
    0x3F13880F: "XECRYPT_RSAPUB_2048",
    0x3F173725: "cEm44ActFly",  # pc-only
    0x3F1885F7: "sCollision::cColArray::MyDTI",
    0x3F18DE8D: "XAUDIO::XAUDIOCHANNELMAPEX",
    0x3F1DDF50: "sEffect",
    0x3F1EFCA2: "CCalAudioEncoder",
    0x3F20ADE2: "_GUID",
    0x3F23C36C: "uWeaponEnemySub",  # pc-only
    0x3F250C93: "HSTR__",
    0x3F2641B5: "SCL1_CRTC_INTERFACE",
    0x3F26ACC1: "MC1_DEBUG",
    0x3F2A197E: "XAUDIO::CFileStream",
    0x3F2B52C4: "NB_SUB_CLASS",
    0x3F2C5DD3: "_FAT_VOLUME_METADATA",
    0x3F322EEA: "XUIMessageFigureVertexPoint",
    0x3F3729D0: "uLight::TYPE",
    0x3F3BEC29: "PCIE_SCRATCH",
    0x3F3CE8AF: "rEffectSetData::ESD_PARAM_CHAIN",
    0x3F3FF5CC: "cEmc0ActErase2",  # pc-only
    0x3F461512: "sLayoutSpr::LSPInfo",  # pc-only
    0x3F47DD99: "D3D::CMicrocodeBuilder::Sink",
    0x3F48EF30: "EFC_KEYFRAME_F32",
    0x3F49FAE2: "uFeedbackBlurFilter",
    0x3F4DC29D: "uOm1316_BackupHeli2::cActBase",  # pc-only
    0x3F521073: "cEm10ActWallHydeL",  # pc-only
    0x3F5223A2: "XUIKeyframeData",
    0x3F555EC0: "_GET_SESSION_RESULTS",
    0x3F575003: "cEm10ActWalkSearch",  # pc-only
    0x3F586DC0: "uSoundStream",  # pc-only
    0x3F6134F2: "XUI_CONTROL_LINK",
    0x3F64A4C5: "FSB_LX_PMC0_OR",
    0x3F6F89DA: "cEm42ActDeathBeatOk",  # pc-only
    0x3F71F0E1: "RB_SIDEBAND_BUSY",
    0x3F7474D0: "EFC_PARAM_U16",
    0x3F74B323: "rTexture::TYPE",
    0x3F76D707: "VIDEOSTREAMINFO",
    0x3F7966A9: "cPlAction_pl_act_test",  # pc-only
    0x3F79D9BF: "uOm1317_Glass::cActBreak",  # pc-only
    0x3F80FAF8: "PIX_CHUNK_TYPE",
    0x3F8358AE: "_CoefStream",
    0x3F86B590: "MC1_SECURE_MEMORY_APERTURE_BASE",
    0x3F8BA902: "_DVD_SPINDLE_SPEED_INFO",
    0x3F8DA085: "SX_PERFCOUNTER0_HI",
    0x3F8E1D41: "NetworkSessionManager::SessionId",
    0x3F8FF48A: "sPrim::Prim::LIGHT_DATA",
    0x3F9994AD: "MtXmlReader::ATTRIBUTE",
    0x3F9C073B: "_XPROFILE_ACTION_MOVEMENT_CONTROL_OPTIONS",
    0x3F9ED1B5: "XAUDIO::CXMASourceEffect",
    0x3F9F68CE: "sPad::CANCEL_BUTTON",
    0x3F9FF37C: "RBBM_DEBUG",
    0x3FA147F7: "uEnvMap",
    0x3FA86330: "uIdCockpit01::Plug",  # pc-only
    0x3FAC0A70: "cEm4502ActErase",  # pc-only
    0x3FAD086C: "sVibration::CameraVibration",
    0x3FADE46C: "rEffectSetData::ESD_SET_FILTER_COMMON",
    0x3FB02892: "uEffectVFR::ClothChain",
    0x3FB3BE70: "BIU_PERFCOUNTER2_HI",
    0x3FB78E04: "_CONSOLE_PUBLIC_KEY",
    0x3FC18649: "cEm84ActSleep",  # pc-only
    0x3FC2FF7D: "_VD_DISPLAY_DISCOVERY_DATA",
    0x3FC9480A: "ORDINAL_TO_INDEX",
    0x3FCA6541: "FSB_LX_LSPARE_OR",
    0x3FCAE3E4: "AZ0_MRU_BANK6_DEPTH_MASK",
    0x3FCD414C: "PA_CL_UCP_5_Z",
    0x3FCDC802: "uOm1316_BackupHeli::cActWait",  # pc-only
    0x3FCDEFCF: "VIDEODECODERSTATE",
    0x3FCF64DC: "_DMALTINI",
    0x3FCF9034: "CCalBase::PLAYER_FLAGS",
    0x3FD08328: "FSB_TLA_PATTERN3",
    0x3FD1038A: "XDVO_REGISTER_INDEX",
    0x3FD18A10: "RB_HSIO_PHASE_SELECT",
    0x3FDAD127: "XCOMPRESS::LZXDECOMPRESS",
    0x3FE29203: "MtCollada::Image::MyDTI",
    0x3FE76ED8: "_DXVA_QmatrixData",
    0x3FE7F841: "_RTL_HEAP_INFORMATION",
    0x3FEBB39F: "sResource::DecompressStream::MyDTI",
    0x3FEF81E4: "CQueue",
    0x3FF1C42C: "uProjectionShadow::transShadow::__l9::SCREEN_VERTEX",
    0x3FF20E5A: "cAITreeBase::Node",  # pc-only
    0x3FF34C3A: "FXLEffectPool",
    0x3FF5BED6: "GC_PMI_PMC_REG",
    0x3FF99995: "rSoundPackageXml",
    0x3FFA9386: "MtCollada::Combiner::MyDTI",
    0x40011C0B: "FSB_LX_DDAT2",
    0x40058359: "CCalBase::__vftable",
    0x4008EB3D: "GPUEXECINSTRUCTIONTYPE",
    0x4009CF95: "MtProperty::Custom::__vftable",
    0x4018FD03: "sCollision::FILTER",
    0x401BCEEC: "_XSTORAGE_ACCESS_TOKEN_READ",
    0x401BF3DC: "MtPreProcessor::BRANCH",
    0x401C8E58: "cEm10ActAtkGunPeepR",  # pc-only
    0x4021604C: "cOmDoorActOpenAuto",  # pc-only
    0x4022C96E: "princeton_digital::float_delay_2",
    0x402BE87A: "cTrans::CMD_RESOLVE",
    0x403686F0: "cPlAction_pl_act_wall_stick_on",  # pc-only
    0x40431EA2: "BIU_PERFCOUNTER3_SELECT",
    0x404492A6: "_ACCOUNT_QUERY_RESPONSE",
    0x404D5D28: "DC_DOUT_DEBUG_MUX_CNTL",
    0x404F23E7: "uOm021c_Switch::cEventActBase",  # pc-only
    0x4050D73E: "_KINTERRUPT",
    0x4051B822: "_XONLINE_MATCH_SESSION_INFO",
    0x40543F55: "_SID_AND_ATTRIBUTES",
    0x40545060: "rEffectSetData::PLACE_TYPE",
    0x405688CB: "IOC_PERFCOUNT_SELECT",
    0x405C32EB: "TCM_PERFCOUNTER1_HI",
    0x405C99EA: "HFONT__",
    0x405D713B: "rChainCol::Header",
    0x406C7C9D: "cNetEm83",  # pc-only
    0x406E7BC7: "_XGSHADER_FETCHCONSTANT_MASKS",
    0x406F609C: "uOma00f_UroPunch::cActWait",  # pc-only
    0x406F8C79: "FSB_TX_PMC4",
    0x40747A32: "D3D::BitVector",
    0x407497F0: "ID10_LUT_DATA_G",
    0x40770FFE: "RCLK_PWRMGT_CNTL_REG",
    0x407859F9: "cEm10ActAtkGunWarnShotR",  # pc-only
    0x407B82BA: "uCoord::MyDTI",
    0x407E2846: "uLight::GROUP",
    0x40820C11: "uEffectVFR::PrimModel",
    0x4082B205: "aS109::cActEvBikeAppear",  # pc-only
    0x4084E824: "sPrim::TransInfo",
    0x4085033D: "PatInterface::LayerPassword",
    0x4085AB99: "PA_SC_VIZ_QUERY",
    0x4088E87F: "cSetInfoOmArea",  # pc-only
    0x408966D6: "_D3DMIPTAIL_DESC",
    0x408A44A5: "uOmElevator::cActWait",  # pc-only
    0x408A70FA: "cEm30ActTurn180",  # pc-only
    0x408E19FF: "_XCONTENT_MEDIA_RESUME_DATA",
    0x408FEF9A: "sSoundN::STOP_TYPE",
    0x40936AC6: "uImageboard",  # pc-only
    0x4095B8D2: "GPUSAMPLECONTROL",
    0x409EE8E4: "CXuiComboBox",
    0x409F67CE: "PACKET_CONTEXT",
    0x40A39B8F: "_XSTORAGE_DELETE_PARAMS",
    0x40AAEC35: "cEm65Action",  # pc-only
    0x40ACA12A: "CODECENTRY",
    0x40AE8995: "cEm20ActAtkExecCatch",  # pc-only
    0x40AEE350: "_WAIT_TYPE",
    0x40B2240F: "_PASSPORT_SESSION_TOKEN_EX",
    0x40B2C1DA: "VGT_VTX_VECT_EJECT_REG",
    0x40B54B15: "DMDATA",
    0x40BCB086: "cScenarioArg_AreaJump",  # pc-only
    0x40BE57C6: "PA_CL_UCP_4_W",
    0x40BED919: "PIX_CAPTURE_FRAME_API",
    0x40C1891E: "_KEXCEPTION_STACK_FRAME",
    0x40C38EDE: "cSetInfoPawn",  # pc-only
    0x40CB8FC5: "CCalOverlappedIoBlock",
    0x40CC9CD8: "_DMTD",
    0x40D5B02F: "BRTSTATE",
    0x40DD1EF9: "cEm34ActMove",  # pc-only
    0x40DD8472: "cEm10ActSitDown",  # pc-only
    0x40DDFA5E: "rSoundSourceEnvironment::MyDTI",
    0x40DE2030: "cPosHokan",  # pc-only
    0x40DF4F0A: "ConfigFrame",
    0x40DFEFD7: "D3D::CQuery",
    0x40E02377: "BIU_INT_BAD_FLUSH_ACK_TAG",
    0x40E80DD6: "uModel::Joint",
    0x40E9D61E: "sCollision::ScrColInfoPreTraverse::MyDTI",
    0x40F5CC8A: "uOmWallStick::cActBase",  # pc-only
    0x40FB8C6E: "_D3DGPUMAJORVERSION",
    0x40FDCF28: "cPlAction_pl_act_item_get_first",  # pc-only
    0x40FE3C1C: "_tag_AMVAEndFrameInfo",
    0x410296A4: "_tiddata",
    0x4103CE79: "_PixDataOpcodesType",
    0x41043568: "LB_DCP_WRITE",
    0x410DF810: "_PLAYTIMERGUIDE_PARAMS",
    0x410EF74A: "rScheduler::TRACK",
    0x41102B60: "VC_PERFCOUNTER1_HI",
    0x41121DD6: "_XMSHORTN4",
    0x411629D8: "CRTC1_DEBUG_05",
    0x4117CF45: "XAUDIO::CEmbeddedList",
    0x411C9C5B: "GPUEDRAMDEPTHFORMAT",
    0x4120D820: "MC1_RDBUF_DATA",
    0x41269032: "GPUALUSRCSELECT",
    0x4126D612: "XUIMessageItemEnable",
    0x412E623F: "uDOFFilter::BLUR_TYPE",
    0x4132006B: "MC0_WR_STR_DLY",
    0x413229EF: "SQ_PERFCOUNTER0_LOW",
    0x41325828: "XML_ATTRIBUTE",
    0x4134A30A: "uBackLight::__vftable",
    0x41351A1E: "CP_ME_RDADDR",
    0x4135ACD0: "RB_COPY_REF",
    0x4135DD18: "_CONTENT_AVAILABLE_RESPONSE",
    0x4137496F: "_VD_DISPLAY_MODE_OVERRIDE_INFO",
    0x41398B84: "uOmCoopSwitch_S301::cActWait",  # pc-only
    0x413C1A01: "MPARAM_WORK",
    0x413CB0DD: "cEm20ActWait",  # pc-only
    0x41402E89: "std::istreambuf_iterator",
    0x414B825A: "sCollision::ScrColInfoCastConvex",
    0x415018C1: "_KSEMAPHORE",
    0x41508BF1: "MP4UserDataAtom",
    0x415651C5: "_MUTANT_BASIC_INFORMATION",
    0x415BBE5F: "PA_SU_DEBUG_CNTL",
    0x4160A9BD: "uOmCoopJumpBroad::cActPlJumpSecond",  # pc-only
    0x4160C03B: "XGI_READSPAINFO_MSG",
    0x4166AE8C: "cPlAction_pl_act_attack_knee_bazooka_second",  # pc-only
    0x4169F5F5: "uOm0933::cActFall",  # pc-only
    0x416B08CD: "ID3DXFileSaveObject::__vftable",
    0x416DBAE8: "_PRESENCE_SET_STATE",
    0x416EA548: "cEmc0ActDamage",  # pc-only
    0x4170E568: "GC_ADAPTER_ID_W",
    0x41769323: "CCalAudioInfo",
    0x4177A65C: "_XGI_CREATESTATSENUM_MSG",
    0x417C3DF1: "PA_CL_UCP_5_W",
    0x417CF8ED: "_SATA_CHANNEL_EXTENSION",
    0x417F29AE: "_XENUMERATORHEADER",
    0x4181A2D0: "XONLINE_ABCH_GET_CONTACTLIST_ITEM_FLAGS",
    0x418498A9: "MtXmlReader::Handler::__vftable",
    0x41897C22: "_ACCOUNT_SET_STATUS_REQUEST",
    0x418D92BE: "PCIE_PERF_COUNT0_SLV_NS_C_CLK",
    0x418E3772: "MtCollada::Library::TYPE",
    0x4194B173: "MtCollada::MyDTI",
    0x4195B20B: "MtGeomConvex::__vftable",
    0x41975AC6: "_XSYSLOADINPUT",
    0x4198E6AF: "NetworkConnectionMcs::InitArg",
    0x419AC448: "EFC_KEYFRAME_AXIS",
    0x419EF923: "uOmCoopJumpBroad::cActBase",  # pc-only
    0x419F661C: "_XUSER_ENUMPLAYER_MSG",
    0x41A4D1E6: "cEm10ActDmgYoro_B",  # pc-only
    0x41A936EA: "FSB_LX_VCARB",
    0x41A9AD44: "cEm83ActDieNormal",  # pc-only
    0x41ADC998: "Direct3D",
    0x41B17A54: "cOmRider2ActDeadExplosion",  # pc-only
    0x41B1AE4E: "PatInterface::CircleUser",
    0x41B52E4C: "direction",
    0x41B5FA1E: "XDVO_2ND_CRC_CNTL",
    0x41B69B07: "cOmWindowAction_wait",  # pc-only
    0x41B8BDE3: "cMaterialStandard",
    0x41BD6613: "uOmCoopSwitch_S301::cActPlPull",  # pc-only
    0x41C66E7F: "uOmJoke::cActBase",  # pc-only
    0x41CA3FBB: "XMEDIA_PLAYER_STATUS",
    0x41CB61EB: "cEm63ActTurn180",  # pc-only
    0x41CFC298: "cEm0bActAtkCatchLoop",  # pc-only
    0x41D3543A: "AZ1_MRU_BANK8_DEPTH_MASK",
    0x41DCCEAF: "sCamera::REGION_MODE",
    0x41DFEB95: "PA_SU_PERFCOUNTER1_HI",
    0x41E455FD: "MtCollisionEpa::MtEpaLocalAllocator::__vftable",
    0x41ECE66A: "RBBM_SOFT_RESET",
    0x41EEDFE2: "_PM4CMDIMLOAD",
    0x41EF5E29: "uOmCoopTreasure::cActBase",  # pc-only
    0x41F4EC1D: "sPhysics::MyDTI",
    0x41F60F75: "XUICacheSceneAsyncThreadData",
    0x41F8C178: "cEm0bActDieFreeze",  # pc-only
    0x41FB859F: "T",
    0x4203C7CC: "cAITerrainAnalyzer",  # pc-only
    0x42056DDB: "cEmc6ActJoint",  # pc-only
    0x4205BD63: "cFSMOrder::FuncParamAngle",  # pc-only
    0x4206B6CE: "rSoundCurveSet::Curve",
    0x4208D6C3: "TCF_PERFCOUNTER4_HI",
    0x42093A5E: "rChain::ChainInfo::CHAIN_TYPE",
    0x420AA8BA: "CP_STQ_RT_STAT",
    0x420BF224: "cEm10ActDeadFaceDownPF",  # pc-only
    0x420C150A: "PartsContactParam",
    0x420FCE5F: "CP_DEFAULT2_PITCH_OFFSET",
    0x42103560: "_RESTRICTED_PRIVILEGE",
    0x421214C1: "CONTENTENCRYPTIONOBJ",
    0x4213ADD8: "_CACHEFILESYSTEM",
    0x42157EB8: "cOma016ActCut00",  # pc-only
    0x42194AD1: "rEffectList::ResourceInfo::STATUS",
    0x421D2D27: "BIOS_15_SCRATCH",
    0x42201987: "AZ1_ZFAIL_SAMPLES",
    0x42256225: "MtXmlReader",
    0x42261858: "NetworkLayer::__vftable",
    0x42262F1D: "D3D::RingAllocChunk",
    0x422BA386: "rAIFSM::Action",  # pc-only
    0x422DB5FC: "MtObject::MyDTI",
    0x422FAC6F: "SQ_CONSTANT_RT_0",
    0x42307113: "PA_SC_CNTL_STATUS",
    0x42355157: "_CACHEHANDLETABLEENTRY",
    0x4237BA87: "RENDERERMSGINFO_SETHORIZSTRETCH",
    0x423C4518: "cEmAction_pl_act_attack_neck",  # pc-only
    0x423E648F: "UCODESHADERTYPE",
    0x424031D7: "XUIMessageControlGetLink",
    0x42412AD7: "uEffectEmitter",
    0x4247DAAB: "CP_NON_PREFETCH_CNTRS",
    0x424B01DC: "BITRATES",
    0x424D53BE: "_MIGRATE_XBOX_COM_USER_REQUEST",
    0x424E69F2: "cPlEventAct",  # pc-only
    0x42509ACE: "NetworkSessionManager::Ping",
    0x42576A2D: "uOmDisp::cActWait",  # pc-only
    0x425930E7: "cEm40ActWalk",  # pc-only
    0x42609E48: "_D3DXKEY_CALLBACK",
    0x42613D5C: "cEm30ActRun",  # pc-only
    0x4262D8D2: "MtCollisionTree::RadixSortMT",
    0x4264885C: "cNetEm8e",  # pc-only
    0x42649CDE: "_UCODE_HEADER",
    0x426D115F: "sEffectVFR",
    0x4270BF64: "GPUGROUPPRIMORDER",
    0x42735652: "_DXVA_TCoefSingle",
    0x42736CC0: "cEm10ActDmgAppearPlagaB",  # pc-only
    0x427698A7: "rEffectList::LINE_TYPE",
    0x4276D68A: "ROM_STATUS_REG",
    0x42773FB4: "_XCONFIG_USER_SETTINGS",
    0x42799165: "uOmJeep::cActPlDmgFire",  # pc-only
    0x428196D9: "VGT_INDX_OFFSET",
    0x428620C9: "NetworkSessionManagerBroadcast::SEARCHRESULT",
    0x4289B9D7: "MtPreProcessor",
    0x4293018D: "sCollision::ScrColInfoFind",
    0x4293A408: "cAIPacket",  # pc-only
    0x42950C2E: "FSB_TX_TERSTM",
    0x429EA5D7: "cPlAction_pl_act_grasp_cliff_second",  # pc-only
    0x42A2EC34: "CP_RT4_MASK",
    0x42A6F64A: "cEm32ActRunBgn",  # pc-only
    0x42A72A4C: "XAUDIO::CSimpleRefCount",
    0x42AB8657: "_PAM_SEND_PIX_COMMAND_EX",
    0x42B1EF4C: "cDemoLogo",  # pc-only
    0x42B30999: "CP_RT_BUFSZ",
    0x42B63CFC: "REG_MACRO_DATA_4",
    0x42B6DE12: "cEm83ActReload",  # pc-only
    0x42B9B46D: "GPUVERTEXFORMAT",
    0x42BBC4A4: "cOmPileAction_dummy",  # pc-only
    0x42BD146F: "cOmCoopGateAction_om_act_closed",  # pc-only
    0x42BF7018: "cOmContainerAction_waitDown",  # pc-only
    0x42BFEF2E: "cEm87Action",  # pc-only
    0x42BFF32E: "SQ_DEBUG_MISC_1",
    0x42C1154B: "VectorOpcode",
    0x42C372AA: "cAIFSMAgent::Core",  # pc-only
    0x42C5053E: "GPUSTENCILOP",
    0x42C93FB7: "D1MODE_V_COUNTER",
    0x42C9780A: "sCollision::NodeGeomInfo",
    0x42C98393: "uOm0912_s119Tram::cActGo",  # pc-only
    0x42D15D8D: "PCIE_DATA",
    0x42D1BC93: "cOmCoopTwistEventPL",  # pc-only
    0x42D50E51: "cEm10ActDeadHeadExplosion",  # pc-only
    0x42D97B13: "cEm20ActOver1M",  # pc-only
    0x42D9ED6F: "CP_RT10_POLL_ADDRESS",
    0x42D9F385: "rEffectList::MyDTI",
    0x42DBBAD1: "PatInterface::LayerInfo",
    0x42E258B3: "D1OVL_UPDATE",
    0x42E35E5F: "_DEVICE_OBJECT",
    0x42E8B671: "CXCabStreamUnpacker",
    0x42EA1758: "XUIMessageShowstate",
    0x42EA36B4: "_XSTORAGE_DOWNLOAD_TO_DIRECTORY_RESULTS_INTERNAL",
    0x42F389F1: "FSB_TX_TERST",
    0x42F3A2AA: "_SECURITY_QUALITY_OF_SERVICE",
    0x42F94950: "cOmJeepAction_om_act_btn",  # pc-only
    0x42FC41C8: "cEm0bDmgAction",  # pc-only
    0x42FF53D3: "cOmBoatAirAction_pl_act_ride_on_cancel",  # pc-only
    0x42FFE755: "sParameter::STAGE_INFO_STRUCT",  # pc-only
    0x43011E26: "VC_CNTL",
    0x430730AC: "_FB_GET_AGG_REVIEWS_RESPONSE",
    0x4309EA64: "FRAME_SKIP_UNWOUND_FRAMES",
    0x430A482F: "cPlAction_pl_act_coop_item_load_second",  # pc-only
    0x430C857E: "uEffect2D",
    0x430CD3D1: "rCollision::MaterialList",
    0x43119CA4: "_D3DXEFFECTINSTANCE",
    0x4311D793: "D3D::SafetyStream",
    0x4312C8BC: "uHemiSphereLight::MyDTI",
    0x431351DD: "sGpuParticle::TransHandler",
    0x43137BF1: "MC0_RD_STR_DLY_0",
    0x431631A0: "cEm84CoreActStrippedEnd",  # pc-only
    0x4317512A: "PatInterface::SearchOption",
    0x43186DF8: "rEffectAnim::SEQ_INDEX",
    0x431A2FEC: "XUIMessageGetTeletypeLocation",
    0x431C4A79: "XCUSTOMACTION",
    0x4320F134: "D1MODE_CHUNK_SIZE_DEBUG",
    0x432BE24F: "_TESTXEXMESSAGE",
    0x4336B150: "rMotionList::MyDTI",
    0x433B3068: "sBioEffect",  # pc-only
    0x433D7B1C: "cHavok",  # pc-only
    0x4341D64B: "EFC_VOLUME",
    0x434404C8: "SB_HEADER",
    0x434732B5: "_D3DVIEWPORTF9",
    0x434E2B14: "cEm61ActTakeOff",  # pc-only
    0x434E37BF: "cPlAction_pl_act_coop_climb_cliff_rescue",  # pc-only
    0x434E5BD7: "IDirectXFileSaveObjectVtbl",
    0x434EAB55: "CXStorageMiscWorker",
    0x434FFF76: "_XPROFILE_SETTING_SYNC_REQUEST",
    0x4350C5AF: "_UCODE_R500_DEBUGGER_HINT_HEADER",
    0x4353CE50: "cPlAction_pl_act_weapon_fire",  # pc-only
    0x4355B3FD: "cPlAction_pl_act_avoid_side",  # pc-only
    0x435B6904: "MP4MovieRecord",
    0x435D79E6: "_P_TEAM_LIST_MEMBERS_MSG",
    0x435E3B88: "MP4SLConfigRecord",
    0x43627D67: "cEm41ActFarCatchOk",  # pc-only
    0x436589A9: "uEffectVFR::UG_UPDATE_FLAG",
    0x436E341F: "cOmBoatAirAction",  # pc-only
    0x436F36D3: "_XMSG_DESTROY",
    0x4379DA42: "uShadowLight::__vftable",
    0x437A3513: "ROM_CLK_REG",
    0x437CE939: "SU_PERFCNT_SELECT",
    0x437D2FA9: "uEm45::cActPlActCrouch",  # pc-only
    0x43853EB8: "cEm10ActAtkGunPeep",  # pc-only
    0x4387E960: "PA_SC_PERFCOUNTER2_LOW",
    0x438ADF81: "uOm0927_Crane::cActMove36",  # pc-only
    0x438CBE85: "rEffectList::EFL_PARAM_LINE_FIX",
    0x438CF142: "_XPROFILE_GAMERCARD_ZONE_OPTIONS",
    0x43918150: "CP_ME_VS_FETCH_DONE_SRC",
    0x43937142: "XHVENGINE",
    0x4395730A: "CCalAudioMetadata::__vftable",
    0x4398F9BF: "MtRange",
    0x439A5EB9: "_IO_COUNTERS",
    0x439BE7F4: "uOma005_Stairs::cActEvBoot",  # pc-only
    0x43A0BD7C: "RB_COLOR3_INFO",
    0x43A12183: "cEm44ActAtckLaser",  # pc-only
    0x43A2CCC4: "RTS_EDGE_0_DY",
    0x43A3F8F7: "_XEX_EXECUTION_ID",
    0x43A6CDA1: "cAIDynamicPathFinding",  # pc-only
    0x43ADD6C9: "cEm10ActBackHoldDmg",  # pc-only
    0x43AFFA1E: "uOm095e_Kick::cActPlBase",  # pc-only
    0x43B3C2C9: "IOC_BSB_MST_REQ_CRC_2",
    0x43B726BC: "CP_ME_VS_FETCH_DONE_ADDR",
    0x43B89FD6: "cMaterialStandard::MyDTI",
    0x43BA9418: "cEm10ActAtkShieldTackle",  # pc-only
    0x43BCBC9C: "uMotionBlurFilter",
    0x43BDEA82: "_D3DLOCKED_BOX",
    0x43BECAAF: "cOmBldgAction_dummy",  # pc-only
    0x43C5F03B: "TP2_CHICKEN",
    0x43C629F5: "_SUB_Q_CURRENT_POSITION",
    0x43CCFADF: "uFade",  # pc-only
    0x43CD381F: "_DVD_XGD2_DISC_AUTH_RESULT_GET_AUTH_PAGE",
    0x43D0092D: "CP_DMA_COMMAND_STAT",
    0x43D09E4A: "cEm10ActIndiJump",  # pc-only
    0x43DCCB78: "cEm32TongueActRelease",  # pc-only
    0x43DEB380: "_XUIDC",
    0x43DFBA89: "IDirectXFileObject",
    0x43E0FB66: "_WMCCommandEntry",
    0x43E100CC: "MC1_STATUS_0",
    0x43E3CB93: "uOm092e_LaserBlock::cActFallen",  # pc-only
    0x43E5A392: "_XCONTENT_DATA",
    0x43EA697B: "VGT_DEBUG_REG3",
    0x43EB9E38: "MC0_PERFCOUNTER0_HI",
    0x43ED8669: "SQ_CONSTANT_T2",
    0x43EDD72A: "CPulseData",
    0x43F29B7F: "TCF_PERFCOUNTER6_SELECT",
    0x43F305CC: "XAUDIO::CSubmixVoice",
    0x43F3F034: "_RTL_PROCESS_LOCK_INFORMATION",
    0x43F48B85: "MtVector4",
    0x43F568CA: "rEffectSetData::SET_TYPE",
    0x43F768C9: "cEm66ActAmbush",  # pc-only
    0x43F7B044: "AZ1_LOOPBACK_LFSR",
    0x43F84280: "_XUPDATE_REFERRAL_RESPONSE",
    0x440484E5: "cEm10ActNeckHang_PL",  # pc-only
    0x4408EB34: "_KSWAP_FRAME",
    0x4409301F: "D1GRPH_UPDATE",
    0x440C6C0C: "_CDCTTableInfo_Dec",
    0x44132CD7: "PA_SC_PERFCOUNTER1_SELECT",
    0x441642BB: "threadmbcinfostruct",
    0x4422D241: "MtRangeF",
    0x442701CC: "rEffectList::CLOTH_OPTION_FLAG",
    0x442C80E9: "_XENUMERATOR_XGI",
    0x442F74B1: "VC_DEBUG_REG8",
    0x4432B242: "_D3DSTATEBLOCKTYPE",
    0x44332B74: "PA_CL_UCP_2_W",
    0x44369E9A: "CP_RT7_MASK",
    0x4437665A: "XUITextFormatInfo",
    0x443847B6: "uOm08e3_RuinTrap::cActPlSuccess",  # pc-only
    0x4439AC7B: "rEffect2D::E2D_LIFE_FRAME",
    0x443B0D36: "cFSMOrder::FuncParamCamera",  # pc-only
    0x443FBFDA: "SQ_PROGRAM_CNTL",
    0x4442286D: "cEm42SActMove",  # pc-only
    0x4446AD17: "XConfigMediaCenterSettings",
    0x444AD742: "MTTraceBuffer",
    0x444D557B: "MC1_PERFCOUNTER0_HI",
    0x44515875: "HZ_PERFCOUNT_SELECT",
    0x4454F3B0: "EFC_PARAM_AXIS",
    0x445AE277: "CContentReferralUpdateRedirect",
    0x445CC53B: "uInfiniteLight::MyDTI",
    0x445D33E7: "PCIE_HDR_LOG0",
    0x446C2F46: "MtCollada::Camera::MyDTI",
    0x4474B233: "TCB_TAG3_DEBUG",
    0x4475E20C: "rEffectList::RANGE_TYPE",
    0x447839B1: "XUIMessageInsertText",
    0x447C7C4E: "MtPropertyList::__vftable",
    0x447F46C5: "sUnit::__vftable",
    0x4484E0C3: "rEffect2D::E2D_HEADER",
    0x4487AD62: "VGT_DEBUG_REG7",
    0x4487EE71: "uEffectEdit::PTCL_COLL_STATUS",
    0x448B1584: "uOmLaserMirror::cActPlLeave",  # pc-only
    0x448C55EF: "PerChannelInfo",
    0x448CE396: "D3D::DecodeTable",
    0x448EEB7B: "sActionButton::ButtonUnit",  # pc-only
    0x4496AD55: "cNetEm4502",  # pc-only
    0x4496E8E2: "NetworkCommunity::NotifyDestination",
    0x44988A9D: "cAIPathCostManager::NodeCostInfo",  # pc-only
    0x4499E46C: "IXAudioEffect",
    0x449CDBF6: "XAUDIO::SRC::Double",
    0x449F13CF: "P_MSG_TYPES",
    0x44A0B1DB: "MP3SI_GRCH",
    0x44A65C41: "_XEX_DATA_DESCRIPTOR",
    0x44A761B7: "cEm42SlimeTargetActWait",  # pc-only
    0x44B6383C: "DCP_CRC_CONTROL",
    0x44B77660: "XECRYPT_HMACSHA_STATE",
    0x44BF5034: "CXMessageSend",
    0x44C00D18: "uOm1303_Truck::cActBreak",  # pc-only
    0x44CAC1B1: "MP4DataReferenceAtom",
    0x44CDF57B: "XGShaderShrinker",
    0x44D2B0E6: "PCIE_PERF_LATENCY_CNTL",
    0x44D32983: "sUnit::MoveLine",
    0x44D8E961: "PMI_CAP",
    0x44D919BB: "AZ1_MRU_BANK4_DEPTH_MASK",
    0x44D979A6: "XUIMessageFocus",
    0x44DC77B3: "uEffectVFR::MatrixParticle",
    0x44E68DAD: "XMALOOPDATA",
    0x44E77AF9: "IXAudioRouterEffect",
    0x44E79E8D: "_XCONTENT_LICENSE",
    0x44EA2C85: "_DXVA_VideoSample2",
    0x44EACDF0: "VGT_CRC_SQ_CTRL",
    0x44EE70F6: "uOma00c_UroAction::cActAB",  # pc-only
    0x44EF4A0B: "_TIME_FIELDS",
    0x44EF54B0: "cPlAction_pl_act_damage_boatair",  # pc-only
    0x44F7138D: "PCIE_VC0_ENH_CAP_HEADER",
    0x44FB0775: "TCD_INPUT2_DEBUG",
    0x44FECED7: "EFC_KEYFRAME_COMMON",
    0x4506ACA6: "cOm0200ActStop",  # pc-only
    0x45080E36: "cEm6dAction",  # pc-only
    0x45181EE9: "GC_BASE_CODE",
    0x451A6C46: "uEffectVFR::MovePathLine",
    0x45203EA6: "SQ_2D_PIXEL_CONSTANT_0",
    0x45206D0D: "CScopeItem",
    0x4528BECB: "RTS_BOUNDBOX_START",
    0x452A0DDD: "_D3DDECLUSAGE",
    0x452B013B: "MtThread::__vftable",
    0x453074A5: "sPhysics::cPhysicsBaseObject",
    0x4531CF7B: "XAUDIOVOICEPACKETCALLBACK",
    0x4534CFD2: "RB_COLOR0_INFO",
    0x45368722: "_GET_PAYMENT_INSTRUMENTS_REQUEST",
    0x454A0C4D: "_DVD_XGD2_DISC_AUTH_RESULT_IO_ERROR",
    0x454CC002: "_FILE_IO_PRIORITY_INFORMATION",
    0x454DDDAD: "ID3DXAnimationSet",
    0x454F1CF7: "XUI_ELEMENT_PROPERTY_TYPE",
    0x4550A0AA: "_FXLSAMPLERSTATEDATA",
    0x4559E150: "NetworkLayer::ServerList",
    0x455D2D10: "cEm10ActWallHydeR",  # pc-only
    0x455EB893: "DCCG_DEBUG_00",
    0x4562CEA2: "rGridEnvLight::NATIVE_FILE_HEADER",
    0x45651A5D: "AHShapeCylinder",  # pc-only
    0x456530B8: "CXuiStringTable",
    0x45674FD1: "cAIPositionEvaluationFuncList",  # pc-only
    0x456F6A2F: "cPositionEvaluationPlayerRange",  # pc-only
    0x456F8578: "CP_RT12_COMMAND",
    0x45736F06: "cEm84ActAtckCatch",  # pc-only
    0x457753AB: "EP_UNUSED_BAR_5",
    0x4577CEA7: "_XSIGNATURE_TO_VERIFY",
    0x4578BAA1: "cOma016ActCut04",  # pc-only
    0x457D82C8: "DC_LUT_SEQ_COLOR",
    0x457E9ED9: "XCOMPRESS::_EncoderBlockInfo",
    0x457FFD64: "XUITimelinePropPath",
    0x45816B24: "_XCONTENT_MOUNTED_PACKAGE",
    0x4581C4B2: "cPlAction_pl_act_attack_knife_licker",  # pc-only
    0x4587CA69: "std::exception",
    0x458A6EAB: "ID3DXAnimationCallbackHandlerVtbl",
    0x458C9087: "MtCollision::SimplexSolver::SIMPLEX_TYPE",
    0x458CAD2E: "ID3DXFragmentLinker",
    0x4591AC93: "_XEX_PAGE_HEAP_OPTIONS",
    0x459772F7: "cPlAction_pl_act_setEventAct_wait",  # pc-only
    0x4597BF67: "CMBColorControl",
    0x459B7575: "cEmc2ActDamage",  # pc-only
    0x45A0C9AF: "WMVDecOutputParams",
    0x45A468EE: "uModel",
    0x45A5E5E8: "XConfigXPlayerSettings",
    0x45A995E6: "CP_SNOOP_CNTL",
    0x45AE4628: "PCIE_RX_TLP_HDR0",
    0x45B05602: "IDirectXFileBinaryVtbl",
    0x45B33B5A: "rEffect2D::GENERATOR_TYPE",
    0x45B3EF05: "_FP_IEEE_VALUE",
    0x45B5136F: "AZ1_SFAIL_SAMPLES",
    0x45B6BC4C: "SurfaceArray",
    0x45B9D397: "_IMAGE_OPTIONAL_HEADER64",
    0x45BCC2C3: "IOC_BSB_SLV_REQ_CRC_0",
    0x45C122CC: "XECRYPT_RSA",
    0x45C193F3: "HCOLORSPACE__",
    0x45C2B751: "uOma005_Stairs::cActEvBase",  # pc-only
    0x45C390D2: "_KTHREAD_STATE",
    0x45C6CA28: "FACIAL_PARAM",
    0x45C7E826: "ID3DXEffectStateManagerVtbl",
    0x45CC326E: "XnSecAssocInfo",
    0x45D0EE26: "uOm090c_BeltShutter::cActBase",  # pc-only
    0x45D23B86: "_XMATCH_SEARCHRESULT",
    0x45D80D18: "FSB_TLA_PATT_CARE_MASK3",
    0x45D82889: "DC_LUTA_BLACK_OFFSET_GREEN",
    0x45D90CA2: "SQ_CONSTANT_2",
    0x45DBF8E5: "REG_MACRO_DATA_0",
    0x45DC863E: "cEm83ActAvoid",  # pc-only
    0x45E50D55: "GPUCmdOpCode",
    0x45E9DEF5: "XG_MCT::_MCTFILE_HEADER",
    0x45EC9B85: "uEffectVFR::LINE_LENGTH_WORK",
    0x45EEF468: "cNetEm6f",  # pc-only
    0x45F14143: "PA_CL_UCP_3_W",
    0x45F1F048: "MP4MovieAtom",
    0x45F405C6: "cEm41AActMissileDive",  # pc-only
    0x45F8639B: "cEm61ActDie",  # pc-only
    0x45F89A08: "PCIE_ROOT_ERR_STATUS",
    0x45FAE4A8: "NetworkLayer::Binary",
    0x45FB6325: "sPrim::PrimType",
    0x45FC5E4B: "cOmDoorActWait",  # pc-only
    0x45FD8B6C: "uEm45::cActPlActHold",  # pc-only
    0x45FF0687: "D3D::BeginShaderConstantData",
    0x45FF263E: "_EVENT_TYPE",
    0x460460B8: "GPUPERFEVENT_MH",
    0x460515A7: "FftDirection",
    0x460671C7: "uOmPlate::cActCrack",  # pc-only
    0x4609604C: "_audecInputBufferInfo",
    0x460992E4: "_LDRX_PATCH_DESCRIPTOR",
    0x461129FD: "XAUDIO::CAutoIrql",
    0x46133E1D: "cEm44ActWalk",  # pc-only
    0x461E5F51: "MP4DataInformationAtom",
    0x46288C0F: "CSpinLock",
    0x462C5155: "std::_Uninitialized",
    0x46319F82: "tWMCDecStatus",
    0x4632D465: "uOmExplosive_Fell::cActBase",  # pc-only
    0x4633376F: "GPUSWIZZLE",
    0x4634EDA0: "_XGIDEALSHADERCOST",
    0x46382025: "rSoundRequest::SOUND_REQUEST_EFFECT_CATEGORY",
    0x46389119: "rEffectSetData::ESD_SET_PRIM_COMMON",
    0x463D7C95: "MCLMSPredictor",
    0x46400D96: "XAUDIOREVERBI3DL2SETTINGS",
    0x4642BCE9: "_XMARKETPLACE_PROPNODE",
    0x464322CE: "CP_RT10_REFERENCE",
    0x46459ECB: "BlendOpX",
    0x4645E3FF: "_P_FIND_USER_REPLY_MSG",
    0x464A14FF: "rEffectList::SE_OPTION_FLAG",
    0x464AB6B5: "_XINPUT_CAPABILITIES",
    0x46532677: "cEm30ActRunBgn",  # pc-only
    0x46540676: "_P_TEAM_MANAGE_TEAM_MSG",
    0x465498D5: "sEffectVFR::MultiRadialBlurFilterControl",
    0x465A9132: "SQ_PS_PROGRAM",
    0x465C73DB: "_D3DCOLORSPACE",
    0x4662CD26: "MC1_DLL_MASTER_ADJ_0",
    0x4665A96C: "CXLivePresence",
    0x46661C74: "cOmCoopBoxAction_om_act_bang",  # pc-only
    0x46685364: "_IMAGE_ROM_OPTIONAL_HEADER",
    0x4669A09A: "cEm40ActUnderGround",  # pc-only
    0x4670999A: "sCapture::TARGET",
    0x4674F888: "_AP21_MEASUREMENT_OUTPUT",
    0x4675952D: "PA_CL_UCP_1_W",
    0x4675DB48: "uActorModel::EffectEmitter::MyDTI",
    0x46764C17: "tm",
    0x467913D5: "cFSMOrder::FuncParamCameraArea",  # pc-only
    0x4679CE2C: "sPhysics::ConstraintParam::MyDTI",
    0x467A8302: "CP_RT15_POLL_ADDRESS",
    0x467BEDC1: "CRTC1_DEBUG_01",
    0x467D22F4: "XACHIEVEMENT_DETAILS",
    0x46810940: "rSoundEngineValue",  # pc-only
    0x46830F47: "tagWMCCodecEntry",
    0x46832814: "DO_TEST_DEBUG_INDEX",
    0x469A4D3B: "MC0_ARBITRATION_CNTL",
    0x469E1139: "cEm0bActStep",  # pc-only
    0x46A2EDAF: "sShader::VERTEX_FILTER",
    0x46AD0039: "MtBlockAllocator::MyDTI",
    0x46B136C7: "XONLINE_SUBSCRIPTION_ENUMERATE_FLAGS",
    0x46B1698A: "cEm30TentacleActDamage",  # pc-only
    0x46B68D34: "DLSSAMPLE",
    0x46B9E196: "cFSMOrder::ScenarioAreaHit",  # pc-only
    0x46B9F6FE: "IXAudioRouterEffect::__vftable",
    0x46C0393F: "cEm0cAction",  # pc-only
    0x46C0F61F: "MtCollada::Element::__vftable",
    0x46C915FF: "cEm10ActDmgYoro_F",  # pc-only
    0x46CA4278: "rEffectList::EFL_MOVE_ADD",
    0x46D3F463: "MtCollada::Extra::MyDTI",
    0x46D513F9: "MC0_PAD_CAL_STATUS",
    0x46D5FA1C: "MOTION_PARAM::USAGE",
    0x46D79A09: "cEm30TentacleActWait",  # pc-only
    0x46D79F81: "uOm1316_BackupHeli::Area",  # pc-only
    0x46D9E6EB: "ID3DXSPMeshVtbl",
    0x46DDD15A: "uJointAnimator::MyDTI",
    0x46E53932: "rEffectList::PRIM_MODEL_AXIS",
    0x46F61879: "TCB_FETCH_GEN_SECTOR_WALKER0_DEBUG",
    0x46F64ACC: "cEm42CActDeathBeat",  # pc-only
    0x46F6F175: "cEm84CoreActDownStripped",  # pc-only
    0x46F750C9: "IOC_PERFCOUNTER3_LOW",
    0x46F7A4DE: "cEm41ActFarPull",  # pc-only
    0x46FE7A4F: "BIUPERFREGISTER",
    0x4701B884: "cNetEm87",  # pc-only
    0x4701F50C: "cEm71ActWait",  # pc-only
    0x47024860: "FSB_TX_PMC0",
    0x47032028: "uOmElevator::cActLeft",  # pc-only
    0x4708DCBC: "uOm0944::cActLiftUp",  # pc-only
    0x47094242: "MtRect",
    0x470C3F42: "_LICENSEE_TYPE",
    0x470D06A1: "_XMSG_INVITE_SEND_PARAMS",
    0x4717B81D: "WRITEBACK_SIZE",
    0x4719C950: "NetworkPeerLive",
    0x471A3F0F: "_D3DHISTENCILCMPFUNC",
    0x472245E6: "cPlAction_pl_act_item_hand_partner_first",  # pc-only
    0x47271A75: "FSB_TR_DEBUG_AUX_OR",
    0x4728D5C6: "cEm42Action",  # pc-only
    0x472A7619: "std::input_iterator_tag",
    0x472AEEE8: "_VERIFY_PARENT_CREDIT_CARD_REQUEST",
    0x472B1BE1: "uInteractiveWater::MyDTI",
    0x472F65EB: "rEffect2D::ResourceInfo::STATUS",
    0x473221A3: "cWind",
    0x473B5FD6: "_HEAP_ENTRY",
    0x47489334: "uOmDive::cActPlDive",  # pc-only
    0x474AF125: "XUI_INTERPOLATE",
    0x474FE628: "MtGeomCylinder::MyDTI",
    0x475128EF: "aS109::cActJeepRideOn",  # pc-only
    0x475338E2: "_TOKEN_OWNER",
    0x475357CA: "rEffectList::MOVE_TYPE",
    0x4754DDBB: "sParameter::SCENO_INFO_STRUCT",  # pc-only
    0x4755EA45: "MtPropertyObject::MyDTI",
    0x475A4479: "STREAMDECODERSTATE",
    0x475AA55A: "_XSECURITY_STATUS_CHECKS",
    0x47611F96: "PA_CL_GB_VERT_DISC_ADJ",
    0x47773BB4: "cEmc2ActCatch",  # pc-only
    0x477915F4: "cEm6cActWait",  # pc-only
    0x477E2884: "uOmCoopSwitch_S301::cActPlReady",  # pc-only
    0x47820AE2: "NetworkMultipleUdp::__vftable",
    0x47849B6D: "rSoundRequest::Element",
    0x4784FC75: "rCommonEffectXml",  # pc-only
    0x478609AD: "_CONTENT_ENUMERATE_RESPONSE",
    0x4787E080: "_XIPTVDVR_PARAMS",
    0x478F5322: "rEffect2D::E2D_PARTICLE_SPRITE",
    0x47921AFE: "_ADDRESS_INFO",
    0x47947B73: "cWpAction_wp_act_weapon_change_ready",  # pc-only
    0x479727F2: "_I3DL2_BUFFERPROPERTIES",
    0x479835AB: "_D3DXSEMANTIC",
    0x479BB6A3: "_XMEMCODEC_PARAMETERS_LZX",
    0x479CE251: "uEffectEdit::PTCL_LIFE_RNO_TBL",
    0x479D3AE6: "_CERTIFICATE_LOG_HEADER",
    0x479D8014: "D3D::CQueryBlock",
    0x479FC177: "cFSMOrderCharacter::FuncParamGoto",  # pc-only
    0x47A0527A: "cTrans::Technique::MyDTI",
    0x47A53D92: "MtPropertyObject",
    0x47A5C9EB: "_XSTORAGE_DOWNLOAD_REQUEST",
    0x47AEC3EE: "_XSESSION_SEARCHRESULT_HEADER",
    0x47AF1D22: "_audecDecodeParams",
    0x47AFD162: "sVibration::VibFlag",
    0x47B13F52: "_P_REJECT_REQUEST_MSG",
    0x47B17ACE: "_PASSPORT_GET_FRIEND_MEMBER_NAME_REQUEST",
    0x47B1A140: "DO_TEST_DEBUG_TRIGGER_CNTL",
    0x47B50FA7: "rAIFSM::ParamArrayProperty",  # pc-only
    0x47B54E02: "SwizzleType",
    0x47B7C3EA: "CP_RT9_BADR",
    0x47B7FF1A: "PA_CL_UCP_0_W",
    0x47B89585: "TCF_PERFCOUNTER2_SELECT",
    0x47BBB932: "CCalVideoPlayer",
    0x47C3585B: "_XMSG_SET_PROP_REQUEST",
    0x47C47EA7: "_XMSG_SEND_RESULT",
    0x47CB3A24: "uOmJeep::cActPlBase",  # pc-only
    0x47CDB479: "_GET_USER_INFO_RESPONSE",
    0x47D48577: "sCamera::Viewport::ATTR",
    0x47D5768B: "AHCameraInfo",  # pc-only
    0x47D68937: "sCollision::RadixSort",
    0x47D73458: "CCalVideoRenderer",
    0x47D7A91C: "uOm0933::cActWait",  # pc-only
    0x47D83A17: "XCOMPRESS::t_encoder_context",
    0x47DE6950: "MtDataReader",
    0x47DF22C4: "AZ1_MRU_BANK0_DEPTH_MASK",
    0x47E426BC: "cTrans::Element::__vftable",
    0x47E4CA71: "MtRay",
    0x47E600A9: "cNetEm60",  # pc-only
    0x47E934E6: "rChainCol::ColInfo",
    0x47EC3C07: "CXStorageDownloadParent",
    0x47ED7F59: "WSAData",
    0x47EF0908: "wmaudio3waveformat_tag",
    0x47F36E4C: "_SYSTEM_ALARM_ACE",
    0x47F9E0A6: "cEm8cAtkArmReturn",  # pc-only
    0x47FC690D: "cEm42ActCoreEnter",  # pc-only
    0x47FDC7CD: "cEm10ActRotate",  # pc-only
    0x47FEDBEC: "RB_TILECONTROL",
    0x47FFA477: "_D3DXSHADER_STRUCTMEMBERINFO",
    0x4800F247: "uInteractiveWater::WATER_VERTEX",
    0x480263C1: "cEm63ActJump",  # pc-only
    0x4802C212: "sCollision::Sbc::__vftable",
    0x4802E440: "FSB_LX_CTRL",
    0x4804AD07: "GPUPERFEVENT_BIF",
    0x480810FA: "CCalStream::__vftable",
    0x480B07DD: "uEm45::cActPlActStagger2P",  # pc-only
    0x480B608B: "FSB_LX_PHYCMD_AND",
    0x480D82CD: "__s_GUID",
    0x480DE2A5: "EHNodeInfo",
    0x480EFFFE: "PCIE_CFG_SCRATCH2",
    0x480F36FF: "RB_STENCILREFMASK",
    0x4810ED77: "cSetInfo",  # pc-only
    0x48123712: "_FB_ENUM_RECD_REVIEWS_REQUEST",
    0x4813DBDA: "_D3DVERTEXBUFFER_DESC",
    0x4815FF8F: "sCollision::ParamGetPolygons",
    0x48187692: "tagNciCodecBlock",
    0x48192F6D: "cEm32ActDieExplosion",  # pc-only
    0x481A7167: "cPlAction_pl_act_grasp_cliff_first",  # pc-only
    0x481B2EA7: "cEm0cPlEvent",  # pc-only
    0x4824F55D: "uOm021c_Switch::cActWait",  # pc-only
    0x4826CB68: "_STFC_CREATE_PACKET",
    0x482732BF: "sArea::__vftable",
    0x482EBEC8: "MtSerializer::PROPERTYDATA",
    0x482F8F7D: "MtCollada::Param::MyDTI",
    0x4831532E: "sPrim::Material",
    0x48321A3F: "XONLINE_VIDEO_TYPE",
    0x48358528: "KCONTINUE_STATUS",
    0x4837AA93: "uOm095a_Jump::cActJump",  # pc-only
    0x4837AE74: "uFacial::jointInfo",
    0x483C1B32: "XAUDIO::CActiveVoiceList",
    0x48446B5A: "EFC_PAT",
    0x48468F06: "XUIKeyFrame",
    0x4849632A: "MP4DescriptorRecord",
    0x484D56E6: "cTrans::TextureBase::MyDTI",
    0x484EE4DB: "IXAudioSourceEffect",
    0x484F3EF3: "uEffectEdit::MovePathCommon",
    0x4850C0E4: "rChain::JointInfo",
    0x485280F5: "rSoundStreamRequest::SOUND_STREAM_REQUEST_COMMAND",
    0x48543114: "AZ0_MRU_BANK5_DEPTH_MASK",
    0x485434FD: "XGI_READSETTINGS_MSG",
    0x48572FD0: "XMSG_CUSTOMACTION",
    0x4860BB48: "cPlAction_pl_act_attack_upper_licker",  # pc-only
    0x48643AA9: "D3D::MEMORYREGION",
    0x48649046: "_FILE_END_OF_FILE_INFO",
    0x4866A5AE: "uEffectEmitter::MyDTI",
    0x486997DD: "ID04_DCP_LB_DATA_REQUEST1",
    0x486C1B18: "_MEDIA_INSTANCE_URLS",
    0x486E1BD7: "PatInterface::ChatOption",
    0x486E8499: "XECRYPT_RSAPUB_4096",
    0x4872C12E: "SamplingRateInfo",
    0x4875EDF7: "NetworkSocket::__vftable",
    0x487A75A7: "tagNEM_AGC_VAD_BLK",
    0x487B93D8: "cOmChainAction_dummy",  # pc-only
    0x487F41C2: "cEm10ActDmgCounterPlagaB",  # pc-only
    0x488040DF: "_DVD_AP25_CHALLENGE_HISTORY",
    0x48805F7B: "_SUB_Q_HEADER",
    0x48871468: "D3D::RenderStateInit",
    0x488759D9: "VGT_OUT_DEALLOC_CNTL",
    0x4887D42E: "cEm60ActDamage",  # pc-only
    0x4887E978: "UVBASE_SWITCHTOVOICECHATPARAM",
    0x488AF941: "cOmCoopBoxAction_om_act_push",  # pc-only
    0x488BC792: "NetworkStorage::FileList",
    0x488E955F: "uOm1307_Boat::cActMove_Start_C",  # pc-only
    0x488EB59A: "_P_ALIVE_2_MSG",
    0x4894F530: "MP4SoundMediaHeaderAtom",
    0x48953DA1: "uEffectEdit::FLAG_CTRL_FLAG",
    0x4895D198: "AIFFFORMAT",
    0x4895F847: "EP_CACHE_LINE",
    0x48A03D38: "CP_RT3_REFERENCE",
    0x48A11BDA: "PatInterface::McsInfo",
    0x48A278C1: "cAIPathCostManager::CostInfo",  # pc-only
    0x48A29FC9: "_COPP_ACP_Protection_Level",
    0x48A43445: "cEm40ActRun",  # pc-only
    0x48A73061: "PREF_BASE_UPPER",
    0x48ABC9A6: "rCameraList::CAMERA_LIST_HDR",
    0x48B1F0BD: "XUIMemoryBuffer",
    0x48B5AD1F: "cAIFSM::ParamConstF32",  # pc-only
    0x48C62BBE: "std::out_of_range",
    0x48CAE5B5: "GPUPERFEVENT_HZ",
    0x48CF67A7: "_ENUMERATE_GENRES_REQUEST",
    0x48CF6AE3: "D3D::CVertexShader",
    0x48CFA244: "MtCollada::Material",
    0x48D5B33C: "EP_GC_MMR_BAR",
    0x48D7B3BE: "FSB_TLA_PATTERN2",
    0x48D9AD10: "rEffect2D::PARTICLE_TYPE",
    0x48DAF418: "NetworkResolver::__vftable",
    0x48DBE452: "sGpuParticle::Context",
    0x48DC67EE: "uChain::MyDTI",
    0x48E711C6: "MtColorHSV",
    0x48EDDBAD: "_PVR",
    0x48F16432: "CP_RT8_POLL_ADDRESS",
    0x48F16739: "MtPropertyList::Iterator",
    0x48F4A4FF: "_D3DMULTISAMPLE_TYPE",
    0x49010CEE: "D1OVL_ALPHA_CONTROL",
    0x49015C84: "uOm090d_Floor::cActBase",  # pc-only
    0x4906A285: "PA_SC_PERFCOUNTER0_HI",
    0x49099703: "_XAUDIOPIXEVENT",
    0x490E68B6: "_D3DSHADER_INSTRUCTION_OPCODE_TYPE",
    0x491D325B: "FSB_TLA_COUNT5_INIT",
    0x4927F7BD: "CReferenceLibrary",
    0x4928CD69: "IDirectXFileDataReference::__vftable",
    0x492BA6AD: "PACKETPARSEINFO",
    0x4933094C: "_RECORDTABLEENTRY",
    0x49338AAA: "MtCollision",
    0x49379266: "TCF_PERFCOUNTER1_SELECT",
    0x49389E22: "CGioBase",
    0x49396911: "uOma004_Collapse::cActPlActBtn",  # pc-only
    0x493A8592: "XAUDIO::CFileStream::__vftable",
    0x493B420A: "_CRT_DOUBLE",
    0x493C1A58: "ScrHideNo",  # pc-only
    0x493D5F70: "SETUP_DEBUG_REG0",
    0x49449565: "PCIE_P_DECODER_STATUS",
    0x4944D804: "NetworkSessionManager::FilterList",
    0x49464EB1: "GC_DEVICE_ID",
    0x494AF8D3: "XConfigDvdSettings",
    0x4961A3B0: "uModel::RenderInfo::LOD",
    0x49680245: "cEm66ActFloat",  # pc-only
    0x496CD7B3: "PA_SU_POLY_OFFSET_BACK_OFFSET",
    0x49720D26: "_D3DCULL",
    0x4972AF0E: "uBioActorPL01",  # pc-only
    0x49732365: "XAUDIO::SRC::NativeVector",
    0x4975429E: "MIDISAMPLE",
    0x497E411E: "rFacialPattern::FACIAL_HDR",
    0x4986203F: "BIU_PERFCOUNTER3_LOW",
    0x49877CCE: "ID3DXKeyframedAnimationSetVtbl",
    0x4988AE3B: "MtCollisionEpa",
    0x498A0C62: "PatInterface::ChargeInfo",
    0x498A9DAC: "_IMAGE_XEX_DIRECTORY_ENTRY",
    0x498BC8D5: "rEffect2D::E2D_KEYFRAME_INDEX",
    0x498EF23C: "_KPROCESS_TYPE",
    0x498F5AC2: "_FB_ENUM_SENT_REVIEWS_REQUEST",
    0x4990CB76: "sExceptionHandler::MyDTI",
    0x49935268: "uProjectionShadow",
    0x4998AE49: "MC1_TIMING_CNTL_0",
    0x4999A0B5: "GPUCompBufferSet",
    0x4999D107: "CDeColorConvParams",
    0x499A493F: "uModel::__vftable",
    0x499A8BE0: "cResource::MyDTI",
    0x499D6DEC: "RTS_EDGE_2_DIST_LSBS",
    0x49A43F8E: "uPointLight",
    0x49A60304: "msaudio1waveformat_tag",
    0x49A7FEBC: "VGT_PERFCOUNTER1_HI",
    0x49A87E8E: "rCollision::Header",
    0x49AC3541: "cEm32ActTurn",  # pc-only
    0x49B50A44: "MtCollada::Perspective",
    0x49BC2016: "rSoundCurveSet::Element",
    0x49BCAB41: "XAUDIO::ASSERT_VALID_LIST_ENTRY",
    0x49C47AE2: "INTRNCVT_STATUS",
    0x49CA2FB2: "PROCMODE_CODEC_INFO",
    0x49CF04CE: "PCIE_PERF_CNTL_SLV_NS_C_CLK",
    0x49D36FC0: "rEffectList::EFL_MOVE_BASE",
    0x49D4C7E1: "cEm8eActWait",  # pc-only
    0x49D519C9: "rEffectList::EFL_PARTICLE_BILLBOARD",
    0x49E221BB: "ID3DXEffectPool::__vftable",
    0x49E30FA8: "D1OVL_ALPHA_OUTSIDE_OVL_WINDOW",
    0x49E5820F: "_XINPUT_RAW",
    0x49E728FA: "cEm32ActSlide",  # pc-only
    0x49EC4600: "sPrim::Rect",
    0x49EC4BB4: "COutputBuffer",
    0x49F129D2: "uFishEyeFilter::MyDTI",
    0x49F5B833: "D1SCL_CRC_MASK",
    0x49F6A6BE: "CCalVideoDecoder",
    0x49F97CD2: "_DXVA_VideoTransferFunction",
    0x49FA6250: "BSB_STATUS",
    0x49FE0987: "_DMXAPI",
    0x49FE595C: "IAMVideoAcceleratorVtbl",
    0x4A000EC1: "CP_RT0_COMMAND",
    0x4A005CA6: "_CREDIT_CARD_INFO",
    0x4A03DB95: "BIF_PERFCOUNTER0_LOW",
    0x4A03FB1A: "_XEKEYEX_INDEX",
    0x4A0569E0: "PatInterface::LayerUserPositionNtc",
    0x4A09B02C: "D3D::InterpolatorTable",
    0x4A0D0B6E: "CP_RT4_SIZE",
    0x4A0E0BBE: "XDVO_DEBUG6",
    0x4A0FB251: "_CACHEHASHTABLE",
    0x4A11F09F: "cEm10ActDmg1m",  # pc-only
    0x4A148574: "cEm44PlEvent",  # pc-only
    0x4A191BD9: "cEm10ActDmgFat",  # pc-only
    0x4A1CE60B: "cPositionEvaluationNearRange",  # pc-only
    0x4A215E79: "_STFC_HASH_ENTRY",
    0x4A2949CF: "MtString::STRING",
    0x4A2AFCA9: "D1CRTC_FRAME_COUNT_START",
    0x4A3203D3: "COHER_DEST_BASE_1",
    0x4A3369F5: "cOmLockActDie",  # pc-only
    0x4A34CB51: "NetworkLayer::MemberList",
    0x4A36AB60: "SX_PERFCNT_SELECT",
    0x4A38D0D9: "_D3DBLOCKTYPE",
    0x4A3EF477: "_D3DXSHPRTBUFFER_DESC",
    0x4A427831: "XUIMessageContentDims",
    0x4A44F57A: "PA_SC_DEBUG_DATA",
    0x4A46E33E: "MtDataWriter::__vftable",
    0x4A4B2346: "_XGSHADER_CONSTANT_MASKS",
    0x4A5BCEFF: "_D3DQUERYTYPE",
    0x4A5C0CEB: "INPUTSRCBUFFERSTATE",
    0x4A5C3188: "cPlAction_pl_act_attack_kick",  # pc-only
    0x4A5C5F48: "CTnsData",
    0x4A5D381C: "IMAGE_LOAD_CONFIG_DIRECTORY32",
    0x4A64E4C1: "_PM4CMDDRAWINDXAUTOINDX",
    0x4A720C0D: "MtLogisticMap::__vftable",
    0x4A73B427: "PMI_CAP_LIST",
    0x4A78A379: "_SECURITY_SEED_AND_LENGTH",
    0x4A7A3884: "sTool::__vftable",
    0x4A7AC2D5: "CCalImagePlayer::ImageRender",
    0x4A7DF1BF: "CSchemaInMemory",
    0x4A807AA0: "ID3DXAnimationController::__vftable",
    0x4A8B6C9C: "sCollision::cNodeListArrayBP::MyDTI",
    0x4A8D35A6: "cEm82AtkDrillDie_PL",  # pc-only
    0x4A8FA66D: "DCCG_BUS_ID",
    0x4A92D0E2: "cTrans::CubeTexture",
    0x4A9544DF: "uEffectGenerator::__vftable",
    0x4A95AD44: "CXuiSceneCache::SceneCacheEntry",
    0x4A9B1E3E: "XAUDIOSRCCHANNELCOUNT",
    0x4A9C2B34: "PA_SC_PERFCOUNTER2_SELECT",
    0x4A9EAB19: "cEm32TongueActCatch",  # pc-only
    0x4AA02B9D: "cEm0bActAtkCatchEnd",  # pc-only
    0x4AA4D9AD: "GPUFLOW_CONSTANTS",
    0x4AA84813: "AZ0_LOOPBACK_TRANSMIT_COUNT",
    0x4AAE2CEB: "D1CRTC_H_BLANK_START_END",
    0x4AB444A3: "_XONLINE_MATCH_SEARCHRESULT_HEADER",
    0x4ABBC64F: "CP_ME_VS_EVENT_DATA_SWM",
    0x4ABBF99D: "aDemo",  # pc-only
    0x4ABD7F72: "cEm83ActBack",  # pc-only
    0x4AC77D9F: "MtCollisionEpa::MtEpaLocalList::TListElem::__vftable",
    0x4ACF2BF0: "D1MODE_VIEWPORT_SIZE",
    0x4ACF9BF1: "CP_ME_SCREEN_EXT_RPT_ADDR",
    0x4ACFB995: "TP0_PERFCOUNTER0_HI",
    0x4AD04892: "cEm40DActEnter",  # pc-only
    0x4AD2E40E: "cEm10ActDmgArm",  # pc-only
    0x4ADA44C3: "cFSMOrder::FuncParamTutorial",  # pc-only
    0x4ADC45A9: "cPlAction_pl_act_die_leave_lie",  # pc-only
    0x4AEAD4A0: "STOP_SCLK_REG",
    0x4AEB0CB1: "MP4MovieFragmentAtom",
    0x4AED9D78: "cEm42TAction",  # pc-only
    0x4AEE3D94: "uOm095c_Break::cActEnd2",  # pc-only
    0x4AEE9E5E: "uModel::MyDTI",
    0x4AF06764: "CCalReadAheadFileStream",
    0x4AF2BF89: "_s_ThrowInfo",
    0x4AF4FC83: "VC_DEBUG_REG0",
    0x4AF6805C: "uOmSwitch3::cActPullRelease",  # pc-only
    0x4AF6847B: "cEm44ActWalkStop",  # pc-only
    0x4AF7619D: "CSystemApp",
    0x4AFC5011: "_XMSG_DETAILS_GET_SUMMARY",
    0x4AFF2D6F: "uOm1307_Boat::cActWait_C",  # pc-only
    0x4B021963: "_FILE_FS_SIZE_INFORMATION",
    0x4B02A49E: "MP4TrackRunEntry",
    0x4B078329: "_PASSPORT_GET_FRIEND_MEMBER_NAME_RESPONSE",
    0x4B08B9E4: "rEffectAnim::ANIM_FLAG",
    0x4B098EF5: "FSB_LX_PMC1_AND",
    0x4B099E0F: "uOm08ed_FirePump::cActStop",  # pc-only
    0x4B12661E: "_P_INVITE_ANSWER_MSG",
    0x4B13B579: "MC0_INTERRUPT_STATUS",
    0x4B174C0E: "DC_TEST_DEBUG_DATA",
    0x4B1910A2: "tagWMVAsyncNotifyInfo",
    0x4B23C6A3: "PIX_REQUEST_PROFILE_CAPTURE",
    0x4B27A403: "cTrans::CMD",
    0x4B2EEA29: "XAUDIOFXREGISTER",
    0x4B2FABDE: "uOm1307_Boat::cActMove_Em",  # pc-only
    0x4B376989: "cPositionEvaluationNearCorner",  # pc-only
    0x4B378FD8: "sRender::Pass::MyDTI",
    0x4B3B9B9B: "sShader::VDECL",
    0x4B441848: "cOmBoatAirAction_om_act_dummy",  # pc-only
    0x4B44375E: "uOm08e9_S303Elev::cActSleep",  # pc-only
    0x4B44E175: "SQ_VS_PROGRAM",
    0x4B48ED3A: "cPlAction_pl_act_coop_treat",  # pc-only
    0x4B49C9AF: "tagWMCDecFileLicParams",
    0x4B520A6B: "AZ0_MRU_BANK1_DEPTH_MASK",
    0x4B54C765: "cPlAction_pl_act_emotion",  # pc-only
    0x4B579228: "_REMEMBEREDFILELISTENTRY",
    0x4B5B71ED: "rSoundCurveSet::NATIVE_FILE_HEADER",
    0x4B5CB3B3: "MtCollada::Program::MyDTI",
    0x4B657484: "cAIFlockFinder::FlockInfo",  # pc-only
    0x4B6F5B20: "cResource::STATE",
    0x4B720CB9: "_DXVA_TCoef4Group",
    0x4B75D5FA: "sRender::RENDERQUALITY",
    0x4B7625F2: "cFSMOrder::FuncParamCameraQuake",  # pc-only
    0x4B78FA44: "ColombDecodeStatus",
    0x4B79DFB4: "XGI_SESSIONCREATE_MSG",
    0x4B7DB87F: "D1MODE_MASTER_UPDATE_MODE",
    0x4B7F4329: "sShader::GEOM",
    0x4B7FD4D8: "_XAM_BOOT_DATA_BLOCK",
    0x4B81A51A: "rAIFSM::State",  # pc-only
    0x4B821B09: "_tagWMVCallBackInfo",
    0x4B825EBE: "FSB_LX_SC",
    0x4B86D469: "MtPreProcessor::REPLACER",
    0x4B8BF1D5: "cEmc3ActDown",  # pc-only
    0x4B8E1104: "uOm090d_Floor::cActDock",  # pc-only
    0x4B8E783C: "_D3DDISPLAYMODE",
    0x4B909449: "SQ_INSTRUCTION_CF_LOOP_0",
    0x4B9727D3: "GPUHISTENCILFUNC",
    0x4B9854BF: "TCR_PERFCOUNTER1_LOW",
    0x4B991229: "CFOpcode",
    0x4B9ECD92: "rEffect2D::E2D_MOVE_ADD",
    0x4BA1D59E: "TP1_PERFCOUNTER0_LOW",
    0x4BA2181B: "DCP_CRC_P0_LAST",
    0x4BA4B999: "cEm41ActMissile",  # pc-only
    0x4BA50712: "rEffectSetData::ESD_HEADER",
    0x4BA6B92C: "PCIE_LC_STATE2",
    0x4BAB4AA0: "cOmCoopGateAction_pl_act_opening",  # pc-only
    0x4BB873D6: "cEm3402Action",  # pc-only
    0x4BC65514: "tagWMVDecodeStatus",
    0x4BCC227A: "sPrim::Material::AlphaOpType",
    0x4BD11A86: "uOmGlass::cActBreak",  # pc-only
    0x4BDB7A69: "pcharNode",
    0x4BDCA3CA: "_XONLINECONTENT_RESUME_STATE",
    0x4BDD8BB3: "cOma016OmEvent",  # pc-only
    0x4BE20AFA: "TP0_PERFCOUNTER0_SELECT",
    0x4BE5238D: "SCL1_DEBUG_BLOCK_ID",
    0x4BE62372: "FSB_TR_DEBUG_HI_OR",
    0x4BE62772: "cFSMOrder::FuncParamKeyItem",  # pc-only
    0x4BE8FE5F: "cTrans::SAMPLERSTATE",
    0x4BEBD560: "GPUPERFEVENT_CP",
    0x4BED2CC0: "HWINSTA__",
    0x4BEE82C8: "rArchivePack",  # pc-only
    0x4BEEF77E: "_DXVA_DeblockIndexAB_H264",
    0x4BF2C90E: "rEffectSetDataList::KF_ID",
    0x4BF43E12: "MtSerializer::CLASSDATA",
    0x4BF4E087: "_XMXDECN4",
    0x4BF831A3: "state_t",
    0x4BFBF84F: "DName",
    0x4BFD4D7D: "cEm41AActBreakLoop",  # pc-only
    0x4BFE8B66: "XCOMPRESS::sha_state",
    0x4C02242C: "sCursor",  # pc-only
    0x4C08F202: "CMp4Reader",
    0x4C0A86C5: "PCIE_VC0_CNTL",
    0x4C0B29CF: "TCA_FIFO_DEBUG",
    0x4C0CB7B6: "_SYSTEM_COMMAND_BUFFER",
    0x4C0DB839: "rScheduler",
    0x4C159E5A: "uEffectEdit::__vftable",
    0x4C1F0224: "_KDEVICE_QUEUE_ENTRY",
    0x4C1F26D1: "MH_CNTL",
    0x4C220CC7: "_PCMFormat",
    0x4C255231: "cEm62ActMove",  # pc-only
    0x4C25F919: "CP4_INT_VECTOR",
    0x4C2BC8BB: "_DXVA_EncryptProtocolHeader",
    0x4C2D404B: "MtCollisionEpa::TExpandPolytopeParam",
    0x4C320BCD: "_NT_PRODUCT_TYPE",
    0x4C324906: "_DMDRIVE",
    0x4C34EFA6: "EFC_KEYFRAME_INDEX",
    0x4C359A11: "_ACCESS_ALLOWED_ACE",
    0x4C3A2C93: "_D3DXMESHSIMP",
    0x4C3A3042: "uOma004_Collapse::cActRun",  # pc-only
    0x4C3E0B18: "BSB_WRAPPER_PRBS23_ERRCNT1",
    0x4C3E6741: "uTextureBlend::MyDTI",
    0x4C497592: "_XPROFILE_SYNC_ACHIEVEMENTS_REQUEST",
    0x4C4A2156: "_STFC_SUICIDE_MODE_PARAMETERS",
    0x4C4B51A0: "_XSIGNATURE_ACKNOWLEDGE_LICENSES_DELIVERY_RESPONSE",
    0x4C4C96BA: "sPrim::Material::AlphaType",
    0x4C514CD5: "_ACL_INFORMATION_CLASS",
    0x4C54A9A0: "rSoundStreamRequest::SoundSource",
    0x4C5556B0: "IOC_BSB_SLV_CPL_CRC_0",
    0x4C5A8277: "uLight::SHFACTOR",
    0x4C60BBA6: "rEffectStrip::STRIP_FLAG",
    0x4C620D95: "cPlAction_pl_act_coop_item_load_stop",  # pc-only
    0x4C62AE64: "rSoundSourceEnvironmentInterMediate::MyDTI",
    0x4C680C81: "MC0_DRAM_DQ",
    0x4C688390: "_FIRMWARE_REENTRY",
    0x4C6A1A55: "sAI::Iterator",  # pc-only
    0x4C6D41E4: "cEm32PlEvent_TongueRelease",  # pc-only
    0x4C6F2DE4: "AZ1_LOOPBACK_PATTERN1PHS3",
    0x4C739265: "MtAllocator::__vftable",
    0x4C767639: "cEm32ActAtkTongue",  # pc-only
    0x4C788857: "_IMAGE_THUNK_DATA32",
    0x4C78D341: "MP4TrackHeaderAtom",
    0x4C797A5E: "sKeyboard::STATE",
    0x4C7B62E8: "ECDDESC",
    0x4C7CA51F: "sShader::TEXDETAIL_TYPE",
    0x4C8693FC: "DECODERINSTANCE",
    0x4C87A1C1: "NB_COMMAND",
    0x4C886622: "_XONLINE_STATS_READ_REQUEST",
    0x4C88FA97: "rEffectList::EFL_PARTICLE_TEXLINE",
    0x4C8B86E6: "tagWMCIndexBlocks",
    0x4C8D68D3: "uOmSwitch3::cActDummy",  # pc-only
    0x4C8E8BB6: "SQ_PERFCOUNTER3_HI",
    0x4C98CB2B: "RENDERERMSGINFO_SETVERTSTRETCH",
    0x4C9979C0: "CP_RT7_SIZE",
    0x4CA26828: "rSoundMotionSe",  # pc-only
    0x4CA3AF66: "SQ_INSTRUCTION_VFETCH_2",
    0x4CACF12A: "PIXMARKERTRACEINFO",
    0x4CB2A688: "rEffect2D::E2D_GENERATOR",
    0x4CB3816B: "cEm84CoreActDownStrippedEnd",  # pc-only
    0x4CB6C607: "LINK_CAP",
    0x4CB8917C: "cEm41ActPunch",  # pc-only
    0x4CB9EAB3: "_DXVA_VideoTransferMatrix",
    0x4CBD2BB1: "cAIFlockManager::ElementInfo",  # pc-only
    0x4CBFF048: "_XGPTC_COMPRESSION_PARAMS",
    0x4CC28298: "uContrastFilter",
    0x4CC6CDAE: "EFC_KEYFRAME_ANGLE",
    0x4CC9ED55: "XUIMessageTimer",
    0x4CCC49BD: "FSB_LR_DEBUG_AUX_OR",
    0x4CD27DC4: "PCIE_PERF_LATENCY_TAG",
    0x4CD46E2C: "_s_UnwindMapEntry",
    0x4CD79FBF: "SCHEMA_UNION_INFO",
    0x4CDB724E: "_D3DTAGCOLLECTION",
    0x4CDBD281: "_KSPECIAL_REGISTERS",
    0x4CDE8F6C: "sPrim::Prim::Packet",
    0x4CE16DED: "SCRATCH_ADDR",
    0x4CE1C6C2: "MP4TimeToSampleAtom",
    0x4CE2F7A9: "uFilter::transImage::__l2::SCREEN_VERTEX",
    0x4CE3C431: "uActorModel",
    0x4CE41F69: "cEm10ActDeadFaceUp",  # pc-only
    0x4CE43050: "MP4TrackReferenceTypeAtom",
    0x4CEB77DF: "aS109::cActJeepEv00",  # pc-only
    0x4CEBA59C: "IOC_INT_ACK",
    0x4CEE1360: "cTrans::Texture",
    0x4CF16BF9: "cEm10ActFind",  # pc-only
    0x4CF8B745: "_XCONFIG_STATIC_ENTRIES",
    0x4CFB9FBC: "MtCollada::Param::TYPE",
    0x4D0207E6: "cEm42CActDamage",  # pc-only
    0x4D03BB22: "_XMSG_DETAILS",
    0x4D070D14: "cOmCoopCardDoorActOpen",  # pc-only
    0x4D0A9E37: "strBinaryStreamInfo_WMC",
    0x4D0B1FC8: "_XSIGNATURE_ACQUIRE_MEDIA_LICENSES_REQUEST",
    0x4D13633D: "DepthFormat",
    0x4D143DB9: "PCIE_CORR_ERR_MASK",
    0x4D14FED0: "cOmJeepAction_om_act_damage_fire",  # pc-only
    0x4D1E3725: "RB_PERFCOUNTER1_HI",
    0x4D1F19B3: "_XINPUT_DEVICE_STATS",
    0x4D1FD47E: "lconv",
    0x4D252335: "XAUDIO::XMA_PLAYBACK_PARSE_ERROR",
    0x4D2644B5: "DRMHEADERINFO",
    0x4D31EC8D: "sEnemy::cLodControl",  # pc-only
    0x4D32A724: "cEm84CoreAction",  # pc-only
    0x4D336AB0: "cTrans::PARAM_DATA",
    0x4D37462B: "AZ1_LOOPBACK_TX_CRC_MASK",
    0x4D38C386: "MC1_TERM_CNTL",
    0x4D38F57B: "uOmElevator::cActCalled",  # pc-only
    0x4D3D8D4E: "uOceanWater::MyDTI",
    0x4D3DC0D6: "cAnimBase",  # pc-only
    0x4D424F01: "D3DXShader::CNodeDecl",
    0x4D4AB33C: "tagUpsampleRefCtl",
    0x4D4CE4F2: "rClothXml::Chain",
    0x4D4D82FA: "uMotionBlurFilter::MyDTI",
    0x4D4F67FA: "FSB_TX_CMDMM1",
    0x4D5E7C95: "AZ0_MRU_BANK9_DEPTH_MASK",
    0x4D5FC7CA: "COHER_DEST_BASE_5",
    0x4D60BD12: "std::num_put",
    0x4D6187B6: "sSoundN::EQ_ENABLE_SW",
    0x4D63CFA7: "XDVO_DEBUG2",
    0x4D68FE79: "ConstraintJointToJointWp2e",  # pc-only
    0x4D6972D6: "TP1_PERFCOUNTER0_HI",
    0x4D6A4194: "TCF_PERFCOUNTER0_HI",
    0x4D6C0C58: "cPlAction_pl_act_die_bomb",  # pc-only
    0x4D6C8891: "sCollision::PartsContactStackData",
    0x4D716E23: "TP1_DEBUG",
    0x4D72F2AF: "CCalImageDecoder::__vftable",
    0x4D73CE8D: "MtCollada",
    0x4D748C2A: "cEm3402ActBlow",  # pc-only
    0x4D75B4B0: "_CEA861_AVI_INFOFRAME",
    0x4D773198: "_D3DXF_FILELOADRESOURCE",
    0x4D7D9C9C: "TCF_PERFCOUNTER5_SELECT",
    0x4D7E468F: "_XASSET_ENUMERATE_RESPONSE",
    0x4D7EA7BF: "_D3DVS_RASTOUT_OFFSETS",
    0x4D833AF9: "CRTC_SCL_INTERFACE_DEBUG",
    0x4D833FA5: "ID3DXSaveUserData::__vftable",
    0x4D84A481: "cNetEm22",  # pc-only
    0x4D85BF96: "cAIFlockFinder",  # pc-only
    0x4D8B282B: "_SID_IDENTIFIER_AUTHORITY",
    0x4D91CB08: "_CONTENT_HISTORY_ENUMERATE_RESPONSE",
    0x4D9398C6: "NCI_CODEC",
    0x4D95B07E: "D1SCL_ONE_SHOT_WATERMARK",
    0x4D965423: "XAUDIO::CStereoRoomFloat",
    0x4D978E58: "D3D::CValidateMemory",
    0x4D982D5E: "IXAudioMasteringVoice",
    0x4D99389A: "VC_DEBUG_REG4",
    0x4D9C4913: "uEffectEdit::MassBillboardKeyframe",
    0x4DA08949: "RB_SAMPLE_COUNT_ADDR",
    0x4DA2AC5E: "MtGeomCylinder",
    0x4DA39A3E: "_IO_STATUS_BLOCK",
    0x4DA3E213: "uEnvMap::CUBIC_BLUR_VERTEX",
    0x4DA5F92B: "sShader::TechniqueDesc",
    0x4DA9678E: "XUIRect",
    0x4DAAD08F: "_exception",
    0x4DADC3A0: "MtCollisionEpa::TEpaFace",
    0x4DBC1CED: "cEm6dActWait",  # pc-only
    0x4DBC3B55: "PIX_INDEX_STRAGGLER",
    0x4DC0A4D6: "DMIF_DEBUG03",
    0x4DC3BBD0: "_LDR_DATA_TABLE_ENTRY",
    0x4DC442EF: "MV1BufferCopyCtl",
    0x4DC50585: "AZ1_PRIMARY_STATE_DWORD0",
    0x4DC70719: "sShader::PIPELINE_SHADOW_CAST",
    0x4DC7C688: "cPlAction_pl_act_item_put_second",  # pc-only
    0x4DC8C306: "_DM_SWAPDISC_START",
    0x4DD4481D: "sShader::FUNC_SHADOW_MASK",
    0x4DD6E3AB: "FSB_TX_TERSTM_AND",
    0x4DD828A1: "MtProperty",
    0x4DDAEAA9: "cAIPositionPickUpWork",  # pc-only
    0x4DE00E08: "XUIQuaternion",
    0x4DE364C8: "_P_TEAM_JOIN_MSG",
    0x4DE8EFA5: "_TESTXEXSYSINFO",
    0x4DEDDCDF: "cEm32Action",  # pc-only
    0x4DEED13F: "MP4TrackRecord",
    0x4DF2A04D: "std::ios_base::Init",
    0x4DF50A6F: "DO_TEST_DEBUG_DATA_TRIGGER_PATTERN",
    0x4E00C2E1: "CP_ME_PS_EVENT_DATA",
    0x4E0146BB: "VGT_GROUP_DECR",
    0x4E0151C8: "_DXVA_PicResample",
    0x4E0861CC: "XAUDIO::CXenonRenderer",
    0x4E0DEFE2: "HSIO_DLL_ADJ6",
    0x4E10C824: "_XMEMCODEC_TYPE",
    0x4E12B807: "_XENUMERATORTITLESERVER",
    0x4E13D190: "aS111::cActJeepRideOn",  # pc-only
    0x4E148683: "D3DBaseTexture",
    0x4E15968A: "AZ0_LOOPBACK_PATTERN1PHS0",
    0x4E1A3877: "ID3DXEffectStateManager::__vftable",
    0x4E1BE1FB: "CCalXmvPlayer",
    0x4E1ECA49: "rSoundReverb::cSoundReverbData",  # pc-only
    0x4E21D46A: "_PERSIST_DISPLAY",
    0x4E25402F: "uBioEffect",  # pc-only
    0x4E262A90: "IO_BASE_LIMIT",
    0x4E26E789: "MH_INT_MASK",
    0x4E27E7B6: "cPlAction_pl_act_walk_l",  # pc-only
    0x4E289993: "std::codecvt_base",
    0x4E2A6C12: "cWpAction_wp_act_reload",  # pc-only
    0x4E2BAF7A: "rCollision::Vertex",
    0x4E2FEF36: "rModelMontage",
    0x4E3002FB: "CG_INT_ACK_REG",
    0x4E3174DC: "DO_TEST_DEBUG_DATA_TRIGGER_MASK",
    0x4E32EB1D: "AZ1_COPY_STATE_DWORD1",
    0x4E33AED8: "CMpegHeader",
    0x4E33CE2C: "MC0_POINTER",
    0x4E348532: "GPU_PROGRAMPACKET",
    0x4E36ECAD: "ID3D10ShaderResourceView",
    0x4E397417: "rEffectAnim",
    0x4E42B995: "SLOT_STATUS",
    0x4E474F9F: "sBioCamera",  # pc-only
    0x4E4CFE9B: "_QUERY_FINDFROMIDS_RESULT",
    0x4E4EBD72: "cFSMOrder::FuncParamGameOver",  # pc-only
    0x4E509B69: "SETUP_DEBUG_REG4",
    0x4E570324: "XG_MCT::MagSign",
    0x4E572D7B: "GPU_WINDOWPACKET",
    0x4E574BD2: "BRTSETTINGS",
    0x4E599229: "uOmPlate::cActBreak",  # pc-only
    0x4E5D26A3: "MtCollisionTree::MyDTI",
    0x4E6254D5: "_Ctypevec",
    0x4E631F74: "CCalMoviePlayer::CreateParameters",
    0x4E6843A7: "rSoundRequest::WriteHeader",
    0x4E6851F6: "GPUPERFEVENT_TP",
    0x4E70EB31: "COMMAND",
    0x4E72FAF3: "uEffectEdit::DIRECTION_FLAG",
    0x4E75BE1D: "TP3_PERFCOUNTER0_LOW",
    0x4E76089D: "XGI_USERSETPROPERTY_MSG",
    0x4E7A01E3: "_STFC_FREE_BLOCK_STATE",
    0x4E7BA172: "_XEX_SECURITY_INFO",
    0x4E81AA54: "cPlAction_pl_act_attack_straight_em10",  # pc-only
    0x4E860C7F: "FSB_TLA_CONDITION3",
    0x4E86E201: "MT_DeBlockCtl",
    0x4E897864: "cTrans::VertexDecl::ELEMENT",
    0x4E8BCCC8: "D3D::CMicrocodeBuilder::Microcode::RenumberRegistersContext",
    0x4E8CAA9E: "sKeyboard::MyDTI",
    0x4E925557: "GPUCmdIntra",
    0x4E96B8B7: "SCRIPTCOMMAND",
    0x4E97DF4B: "uOm0927_Crane::cActMove63",  # pc-only
    0x4E9AE023: "cEm30PlEvent_NeckBiteMissTH",  # pc-only
    0x4E9E90C8: "_VERIFY_INFORMATION",
    0x4E9EEF8A: "D1CRTC_BLACK_COLOR",
    0x4EA2CD02: "ID3DXMatrixStackVtbl",
    0x4EA385CB: "rEffect2D::E2D_MOVE_COMMON",
    0x4EA6B324: "cEm84ActAtckAshibarai",  # pc-only
    0x4EAA746A: "GC_CAPABILITIES_PTR",
    0x4EB5CFB4: "_DM_ODD_READ_REQUEST_DATA",
    0x4EBB53BD: "CSite",
    0x4EBE2577: "CP_STATE_DEBUG_INDEX",
    0x4EC80CAF: "MC1_RD_BUFFER_CNTL_1",
    0x4EC956B1: "_IMAGE_ARCHIVE_MEMBER_HEADER",
    0x4ECB1FBD: "cPlAction_pl_act_plaga_stick_out",  # pc-only
    0x4ECC1941: "BIU_PERFCOUNTER0_SELECT",
    0x4ED14A57: "FACIAL_PARAM::USAGE",
    0x4ED26254: "cOmDoorEventEM",  # pc-only
    0x4ED72B49: "VC_CNTL_STATUS",
    0x4ED8A797: "ID3DXFile",
    0x4EDA1089: "XAUDIO::CStaticBatchAllocator",
    0x4EDC7B17: "PCIE_RX_DLLP_CRC",
    0x4EDF18C3: "uModel::Joint::MyDTI",
    0x4EE6F834: "FSB_LR_DEBUG_LO_OR",
    0x4EEAF84D: "cEm10ActAtkTorchFire",  # pc-only
    0x4EEE38CE: "uOm1303_S109_Truck::cActBreak",  # pc-only
    0x4EF1D34A: "_OSVERSIONINFOA",
    0x4EF5563B: "_KPROCESSOR_STATE",
    0x4EF89C91: "GPU_INTBAR",
    0x4EFAD087: "Ressource_type",
    0x4EFB3DF3: "GC_REGPROG_INF",
    0x4F01AD5E: "_XPROFILE_GAMER_YAXIS_INVERSION_OPTIONS",
    0x4F02D751: "cEm4502ActDie",  # pc-only
    0x4F066D4D: "HGLRC__",
    0x4F07C0AB: "CAP_PTR",
    0x4F0A3F34: "CHuffmanDecoder",
    0x4F121BCC: "_XNQOSPROFILE",
    0x4F14B4D3: "XGI_WRITEACHIEVEMENT_MSG",
    0x4F17AB93: "PA_SC_ENHANCE",
    0x4F1A9D6D: "sNetworkLibrary::__vftable",
    0x4F231C4B: "_DVD_XGD2_DISC_AUTH_RESULT_CHALLENGE_REQUIREMENT",
    0x4F23C266: "CP0_INT_VECTOR",
    0x4F27E26E: "uOmJeep::cActWepActBtn",  # pc-only
    0x4F27F83D: "BIU_PERFCOUNT_SELECT",
    0x4F27FB50: "D3D::BufferResourceNode",
    0x4F32DAB6: "uRefWater",
    0x4F34E8E1: "rEffectList::PRIM_MODEL_TYPE",
    0x4F3592D3: "FPARAM_VECTOR3",
    0x4F37832D: "PIX_ESTIMATE_VIDEO_COST",
    0x4F3A1FCE: "cSubAction::Motion",  # pc-only
    0x4F3A6272: "EHExceptionRecord::EHParameters",
    0x4F42153F: "XUIMessageCheckState",
    0x4F435F6B: "MtCollada::Imager::MyDTI",
    0x4F49D775: "rEffect2D::E2D_PARTICLE_TEXLINE",
    0x4F51D878: "ID3DXAnimationCallbackHandler::__vftable",
    0x4F525FB6: "cEm83ActReadyEnd",  # pc-only
    0x4F5CD087: "cOmLadderAction_climb",  # pc-only
    0x4F5EFC68: "rVibration::VIB_CAM_SINGLE",
    0x4F5F3874: "IPersistStream",
    0x4F6345E0: "_I3DL2_OCCLUSIONPROPERTIES",
    0x4F643AED: "BIOS_0_SCRATCH",
    0x4F6B65C7: "CP_RT15_BADR",
    0x4F6D5600: "tagSESSION_STRUCT",
    0x4F722ADC: "sGpuParticle::PacketVB",
    0x4F725A61: "cEmActInterpolation",  # pc-only
    0x4F736118: "uEffectVFR",
    0x4F7F3487: "NB_CACHE_LINE",
    0x4F80257D: "_FP128",
    0x4F82735E: "SQ_INSTRUCTION_CF_EXEC_0",
    0x4F87B923: "_XGUCODE_DESCRIPTION",
    0x4F8EA67E: "uFlowingWater::MyDTI",
    0x4F93F5EB: "CPnsStaticInterChannelData",
    0x4F96ADAD: "sSoundN::EFFECT_TYPE",
    0x4F9B4441: "_XSYSLOADOUTPUT",
    0x4FA18F10: "cEmc3ActDie",  # pc-only
    0x4FAD1ECA: "FHdrDecodeStatus",
    0x4FB10B5F: "uColorFogFilter::MyDTI",
    0x4FB3572C: "DISP_RBBMIF_RDWR_TIMEOUT",
    0x4FBC53EC: "MtSpline::__vftable",
    0x4FCB8BB0: "FSB_LX_DEBUG_AUX_AND",
    0x4FCE9F7A: "cEm0cActHover",  # pc-only
    0x4FCF3AEB: "cEm34ActCoreMove",  # pc-only
    0x4FCF441E: "MtLogisticMapCycle",
    0x4FD22280: "cEm41ActFarCatch",  # pc-only
    0x4FD48B88: "_XMSHORT2",
    0x4FD7A652: "D3D::CMicrocodeBuilder::Microcode::CreateVSOutputPatchesContext",
    0x4FD989A3: "XUIImageInfo",
    0x4FDF3281: "uEffectVFR::MoveMul",
    0x4FE1D785: "D3D::CMicrocodeBuilder::Pass",
    0x4FF0D1D7: "CXuiElementImplBase",
    0x4FF829EB: "sKeyboard",
    0x4FF8E97B: "uEffectVFR::PARTICLE_DRAW_PARAM",
    0x4FFACBA4: "_CONTENT_HISTORY_INFO",
    0x4FFEC5D6: "VertexMode",
    0x4FFF4A6A: "_D3DCLIPSTATUS9",
    0x50014A57: "PA_CL_UCP_4_X",
    0x5004E746: "SQ_PERFCOUNTER0_SELECT",
    0x5007C03B: "cEm41ActFarEscape",  # pc-only
    0x500BA060: "HdrDecodeFltParCDLMSStatus",
    0x501613BF: "cEm44ActHover",  # pc-only
    0x502298ED: "PIX_XAM_COUNTERS",
    0x5029FF1B: "uBlurFilter::MyDTI",
    0x502B368B: "MP4HintMediaHeaderAtom",
    0x502CB75A: "RBBM_INT_CNTL",
    0x50314F5D: "rSoundSourceXMA::XMA2STREAMFORMAT",
    0x50340ECA: "SETUP_DEBUG_REG3",
    0x5036C341: "CXStorageUploadParent",
    0x5039818A: "XGI_SESSIONSEARCHBYIDS_MSG",
    0x504136E6: "std::_Secure_char_traits_tag",
    0x50458FD2: "uAdhesion::PIPELINE",
    0x5049EE8B: "tagDeBlockCtl",
    0x504A29EB: "TCO_QUAD0_DEBUG1",
    0x504B905D: "EVENTHANDLERID",
    0x50564962: "IptoStateMapEntry",
    0x5056C486: "uOmS705ceil::cActBase",  # pc-only
    0x5057EC28: "uOma004_Collapse::cActPlBase",  # pc-only
    0x5058179F: "matlab_vect",
    0x505834B9: "cEm84ActWait",  # pc-only
    0x505892CF: "FSB_LX_LFIRST",
    0x505A5E6F: "PIX_INDEX_GPU_TIMING",
    0x505F0060: "_ACL_SIZE_INFORMATION",
    0x5062FB62: "MP4VideoMediaHeaderAtom",
    0x50655044: "XMA2STREAMFORMAT",
    0x50697A41: "HSIO_DLL_ADJ1",
    0x506AA00B: "_XMATCH_SESSION_CREATE_REQUEST",
    0x506E05F2: "XAUDIO::CRiffChunk::__vftable",
    0x506E1F8B: "_XPROFILE_CLEAR_ACHIEVEMENTS_REQUEST",
    0x5070683E: "uShadow::SHADOW_TYPE",
    0x507091F4: "cPlAction_pl_act_damage_get_up_front",  # pc-only
    0x5073DDD4: "_PASSPORT_GET_USER_DATA_RESPONSE",
    0x5074D923: "AZ1_MRU_DEPTH_MASK",
    0x5076D2CA: "uEffectEdit::PolygonKeyframe",
    0x50798786: "_DM_CMDCONT",
    0x507AE14F: "cEm61ActWait",  # pc-only
    0x507DE156: "sSoundN::SeVoice::ADSR_STATUS",
    0x507E1483: "PA_CL_POINT_SIZE",
    0x507E743D: "cEm10ActAtkSpearBig_PL",  # pc-only
    0x507F0BED: "RTS_EDGE_1_DIST_LSBS",
    0x508B5D91: "timeval",
    0x5091FFF3: "MC1_TIMING_CNTL_3",
    0x5097FDDB: "_SGADDR2",
    0x5099626C: "rModel::RCN_HEADER",
    0x509C1E56: "XDVO_REGISTER_DATA",
    0x50AA5404: "_D3DLOCKED_TAIL",
    0x50AD8D85: "_FP__IEEE_ROUNDING_MODE",
    0x50AEDAC5: "cShape::WeightNode",
    0x50B7C4EF: "cEm40Action",  # pc-only
    0x50BCACF3: "rModel::RCN_TRIANGLE",
    0x50BD792D: "TCF_PERFCOUNTER7_HI",
    0x50C4C7B6: "_XFILECACHESTATS",
    0x50C53E84: "_D3DVERTEXELEMENT9",
    0x50C7F011: "XUI_ITEMCOUNT",
    0x50C94337: "uFlatWater::MyDTI",
    0x50C96DAF: "_FILE_COMPLETION_INFORMATION",
    0x50CCACFF: "cOmCoopDoorAction_om_act_push",  # pc-only
    0x50D2042F: "CCalTiffDecoder",
    0x50D430ED: "cFSMOrderEm34::FuncParamEm34Start",  # pc-only
    0x50D6F650: "cEmA2ActGunReady_PL",  # pc-only
    0x50D85649: "cOmPileAction_wait",  # pc-only
    0x50D956DA: "_KOBJECTS",
    0x50DCC945: "XAUDIO::XMA_PLAYBACK_INIT",
    0x50E299DC: "FSB_TLA_CONDITION4",
    0x50E2DC33: "AZ0_TOTAL_SAMPLES",
    0x50E35B55: "D3D::Hang",
    0x50EDAD59: "PA_CL_POINT_Y_RAD",
    0x50F74604: "AZ0_MRU_BANK0_DEPTH_MASK",
    0x50F7AFCD: "std::_Range_checked_iterator_tag",
    0x50F9DB3E: "rShader",
    0x50F9E0C9: "XConfigConsoleSettings",
    0x50F9F877: "cEm30ActFall",  # pc-only
    0x50FCBF92: "r2Texture",
    0x5100DC2B: "XG_MCT::DNode",
    0x5103CAE9: "CCalPcmDecoder",
    0x5107AE44: "PCIE_CFG_SCRATCH1",
    0x51086CF7: "cPlAction_pl_act_provoke",  # pc-only
    0x5109A809: "IXHVEngineVtbl",
    0x510CB03C: "_FILEIOHOOKS",
    0x510ECA8A: "_XONLINE_STATS_ENUM_BY_RANK_REQUEST",
    0x51114368: "_STF_DIRECTORY_ENTRY",
    0x51124481: "cMaterial::__vftable",
    0x5119C075: "uOm08b8_Limited::cActClose",  # pc-only
    0x511B1759: "NetworkSessionManagerBroadcast::MemberInfo",
    0x511C4697: "_COPP_ImageAspectRatio_EN300294",
    0x511CF20F: "cEm20ActBack",  # pc-only
    0x512B7933: "rEffectList::CLOTH_WAVE_FLAG",
    0x512BA72B: "cEm10ActLanding",  # pc-only
    0x5130BDBE: "D1SCL_COEF_RAM_TAP_DATA",
    0x51360BB6: "_FILE_INTERNAL_INFORMATION",
    0x51379B88: "XGI_USERSETCONTEXT_MSG",
    0x51394971: "D3dGpuDrPixCounters",
    0x513A758D: "SQ_DEBUG_MISC",
    0x513D8060: "rClothXml",
    0x513F233A: "FSB_LX_PHYDATA_OR",
    0x51425B39: "CP_RT0_REFERENCE",
    0x5143D0E6: "GpuIntComp",
    0x51485092: "cEm84ActWideFire",  # pc-only
    0x5149D197: "CXStorageDownloadParent::__vftable",
    0x514DDFB7: "sArea",
    0x514F943A: "BIU_INT_VECTOR",
    0x5151DCDC: "XAUDIO::CPoolMemoryManager",
    0x515261CF: "cOmBoatAirAction_om_act_ride_off",  # pc-only
    0x51534FD9: "_HVX_IMAGE_XEX_HEADER_API",
    0x51535BA2: "uOm1316_BackupHeli2::cActPoint",  # pc-only
    0x5164881F: "_DVD_XGD2_DISC_AUTH_RESULT_GET_NEXT_CHALLENGE",
    0x5171B402: "BIF_PERFCOUNTER0_HI",
    0x51728AF8: "t_SpatialPredictor",
    0x51740F1F: "uRefWater::MyDTI",
    0x51758AFF: "cPlAction_pl_act_wall_stick_off",  # pc-only
    0x5176977C: "MC1_PAD_IF_CNTL",
    0x51780DC7: "ID3DXFileSaveDataVtbl",
    0x5178E77A: "_IRP",
    0x517A3504: "rEffectList::ResourceInfo",
    0x517C34A2: "sCollision::SCROLL_MOVE_MAT_ID",
    0x517EBE91: "_SE_IMPERSONATION_STATE",
    0x5180466E: "CG_INT_STAT_REG",
    0x5183F96B: "cEm10ActRiseFaceDown",  # pc-only
    0x51885F98: "XUIFontMetrics",
    0x51892366: "_XCONTENT_METADATA",
    0x518AF1BF: "uOmJeep::cActPlActEv00",  # pc-only
    0x519260D5: "uOmSpileTrap::cActDown",  # pc-only
    0x519376A8: "cAIPathCostManager",  # pc-only
    0x519C4978: "CP_RT0_SIZE",
    0x519DF5AE: "_CACHEFILETABLEROOTENTRY",
    0x51A3E35A: "_XMATCH_SESSION_DELETE_REQUEST",
    0x51A6F23C: "_TEAM_ENUM_RESULTS",
    0x51AAB56D: "_KTIME_STAMP_BUNDLE",
    0x51ACBD8B: "CP_RT_ST_BASE",
    0x51AFC138: "uOmObjAdjust::cActWait",  # pc-only
    0x51B1959D: "uCamera",
    0x51B334B3: "CopyFmtCommand",
    0x51B5EC8C: "_FPIEEE_RECORD",
    0x51BB9611: "sCollision::cNodeListArrayBP",
    0x51BF8A5F: "rCameraXml",
    0x51C0EC78: "_ACCOUNT_VERIFY_BILLING_INFO_REQUEST",
    0x51C32060: "PA_CL_UCP_5_X",
    0x51C8D563: "VOICECHATSTATUS",
    0x51CE622B: "sockaddr_in",
    0x51CE7E85: "tagPackHuffmanCode_WMV",
    0x51D664E8: "MtCollada::Rotate",
    0x51D6B930: "GPUPERFEVENT_MC",
    0x51D8384E: "std::basic_ostream",
    0x51DA1C6F: "_SPIF_NOTIFICATION",
    0x51DEE204: "FSB_TLA_PATTERN1",
    0x51E5958B: "MP4MediaDataAtom",
    0x51E97A57: "sSoundN::EQ_FILTER_TYPE",
    0x51EF3D90: "std::bad_cast",
    0x51F0C7A7: "MP4MediaAtom",
    0x51F31FC9: "_WSABUF",
    0x51F46A7F: "_P_INVITATION_ITEM",
    0x51F67C1B: "MP4PrivateMovieRecord",
    0x51FA06B8: "rEffectAnimation::__vftable",
    0x51FC779F: "rCollision",
    0x51FE6204: "NetworkCommunity::__vftable",
    0x5201BB81: "_DMINIT",
    0x5204D557: "rShape",
    0x5207698A: "PCIE_ADV_ERR_CAP_CNTL",
    0x5209EB47: "Tokens",
    0x520A01F9: "D3D::FixupRecord",
    0x520B47E3: "_XUSER_ONLINE_PROFILE_SETTING",
    0x520DAA64: "cEm34ActWait",  # pc-only
    0x5214913B: "CP_RT13_COMMAND",
    0x5219E3C4: "uOm095a_Jump::cActPlEscape",  # pc-only
    0x522A95CA: "cTrans::TECHNIQUE",
    0x522DE8CE: "PCIE_PERF_LATENCY_MAX",
    0x522E1E7E: "rSoundRequest::MyDTI",
    0x522F7A3D: "rFacialPattern",
    0x523457AA: "PCIE_RX_DLLP1",
    0x52345C88: "cEm30ActWalkEnd",  # pc-only
    0x523A4857: "D3DLineTexture",
    0x523FA9F8: "_XUPDATE_DOWNLOAD_PARAMS",
    0x52407FF1: "CCalStream::ACCESS",
    0x52410B7D: "PatInterface::UserBinaryNtc",
    0x52433896: "GPUCmdCopyFrame",
    0x524B46BD: "_XWMDRM_CREATE_CERTIFICATE_REPLY",
    0x524B4AEC: "PCIE_TX_CNTL",
    0x52567A66: "D1CRTC_V_SYNC_A",
    0x5258CC84: "cAIFSM::ParamConstS32",  # pc-only
    0x525C79F7: "sSoundN::FAST_FADE_STATUS",
    0x525CC78E: "cEm32ActAppearWalk",  # pc-only
    0x52606BCC: "MBType",
    0x52614110: "_D3DSWAPEFFECT",
    0x526598AA: "cFSMOrder::FuncParamBossMark",  # pc-only
    0x526772B2: "cEm63ActDie",  # pc-only
    0x526918DB: "uColorCorrectFilter::trans::__l16::SCREEN_VERTEX",
    0x526B1904: "MtObjectGroup::MyDTI",
    0x526C1DBE: "uSpotShadowLight::MyDTI",
    0x526CCD30: "uEffectEmitter::CONTROL_FLAG",
    0x526E557F: "CP_RT12_BADR",
    0x5271EECF: "CP_ME_STATUS",
    0x52748BEA: "uOm1303_S109_Truck::cActWait",  # pc-only
    0x527558C4: "cEm8cActTurn",  # pc-only
    0x5278F885: "SYSUIINIT",
    0x527B63EF: "RBBM_CRC32",
    0x5285B651: "cPlAction_pl_act_boatair_wait",  # pc-only
    0x5285C92E: "CompareRef",
    0x5286AEEB: "ID3DXSprite::__vftable",
    0x5286E8A9: "ISequentialStreamVtbl",
    0x528B7843: "RTS_Z_MIN",
    0x528C704D: "FSB_TLA_COUNT1_INIT",
    0x528D1952: "cEm62ActDieBlow",  # pc-only
    0x528EB35C: "cEm65ActFall",  # pc-only
    0x5290393F: "SCLK_PWRMGT_CNTL1_REG",
    0x5293627F: "NetworkSessionManagerLive::PropertyMap",
    0x5294A40C: "XCOMPRESS::_XMEMCODEC_CONTEXT_HEADER",
    0x5295B212: "RTS_I_W_DX",
    0x52960667: "D3DResource",
    0x52971F1F: "cEm6fAction",  # pc-only
    0x529B2345: "MC0_CRC_CNTL",
    0x52A7E9FC: "VOICECHATINFO",
    0x52AA8A53: "XUINamedFrame",
    0x52ABA14A: "cOmBoltActWait",  # pc-only
    0x52AC89E2: "rEffect2D::KEYFRAME_TYPE",
    0x52AE07D2: "PCIE_PERF_LATENCY_TIMER_LO",
    0x52AF0DCD: "tagVideoFormat_WMC",
    0x52AFE896: "PCIE_LC_STATE1",
    0x52B34094: "rVibration::VIB_COMMON",
    0x52B500AE: "cTrans::DRAWSTATE",
    0x52B626AE: "sCollision::GEOM_BUF_ID",
    0x52BB3223: "D3D::CParser",
    0x52BE9E41: "_D3DXKEY_VECTOR3",
    0x52BEB667: "uOm0927_Crane::cActMoveCD",  # pc-only
    0x52C0B5B9: "CERT_DER_ENTRY",
    0x52C130CD: "_FXLPASSENTRY",
    0x52C32F58: "SCHEMA_TABLE_ENTRY",
    0x52C5CB15: "cMaterialStandard::FUNC_SPECULAR",
    0x52C65AAF: "uEffectVFR::ClothPolygon",
    0x52C6861D: "_P_DEAD_USER_MSG",
    0x52C72BC9: "std::_String_base",
    0x52C7AC67: "cEm84ActAtckAshibaraiHit",  # pc-only
    0x52C889EC: "errentry",
    0x52CB0623: "cEm43ActThreatA",  # pc-only
    0x52CD5EF2: "sCollision::ScrColInfoAdjustPosition",
    0x52CFE70A: "cEm10ActAtkGunBlow",  # pc-only
    0x52D3B261: "sRender::LODOFFSET",
    0x52D40310: "rSoundEQ::cEQData",  # pc-only
    0x52D89B10: "D1COLOR_SUBSAMPLE_CRCB_CNTL",
    0x52DB7B9E: "DC_PERFCOUNTER0_HI",
    0x52DBD75C: "cEm44ActRunEnd",  # pc-only
    0x52DCE33B: "cEm32PlEvent_TongueRescue",  # pc-only
    0x52DF9837: "PCIE_P_PAD_FORCE_DIS",
    0x52F528CD: "RB_PERFCOUNTER0_LOW",
    0x52F59BD5: "_XCONTENT_VOLUME_TYPE",
    0x52F8B45E: "cFSMOrder::FuncParamCollision",  # pc-only
    0x53026EC8: "uOm095d_Stampede::cActPlStamped",  # pc-only
    0x53048FC5: "SurfaceTiling",
    0x53075A04: "XDVO_DEBUG5",
    0x5309000F: "cEm84ActDieBlow",  # pc-only
    0x530F953A: "XUIMessageSetScrollBarItemData",
    0x53132AE9: "sShader::TEXFILTER_TYPE",
    0x5327FDE0: "uOm095d_Stampede::cActWait",  # pc-only
    0x532ED804: "MtCollada::Vertices::MyDTI",
    0x5334ACD8: "_XNQOSMEASUREMENTS",
    0x5339F620: "MtPreProcessor::REPLACER::TYPE",
    0x533B27DD: "_XBMOVIE_CAPTURE_FRAME_INFO",
    0x533B5269: "COHER_DEST_BASE_2",
    0x533F4B74: "TCR_CHICKEN",
    0x5342B248: "uOm08e3_RuinTrap::cActPlFall",  # pc-only
    0x53444084: "_XPERSISTENTMEMBUFFER",
    0x5345D77F: "IAMVideoAcceleratorTag",
    0x5347E16E: "GPUCONSTANTTYPE",
    0x5348D5BD: "tagWMADateParams",
    0x5348E2BC: "NetworkSessionManager::PropertyList",
    0x534F7200: "GC_CACHE_LINE",
    0x53530700: "IOC_BSB_MST_CPL_CRC_1",
    0x53581AA8: "cOmBoatAirAction_om_act_crash",  # pc-only
    0x5359D3A3: "DC_TEST_DEBUG_OUT_CNTL",
    0x5359E505: "cEm10ActTakeWeapon",  # pc-only
    0x536415C7: "D1GRPH_X_END",
    0x5364165C: "TCD_INPUT0_DEBUG",
    0x536565F3: "sLight::__vftable",
    0x536A447B: "PA_SU_PERFCOUNTER2_HI",
    0x53704FEC: "rSoundPackage::Header",
    0x5373471B: "_CREATE_LIVE_ACCOUNT_RESPONSE",
    0x53742DAF: "_WIN32_FILE_ATTRIBUTE_DATA",
    0x53769219: "CP_ME_CF_EVENT_DATA",
    0x53783AD4: "MtGeometry",
    0x537970B6: "cOmCoopGateAction_om_act_dummy",  # pc-only
    0x537A911E: "uFilter::BLEND_TYPE",
    0x537B10F3: "VGT_DEBUG_REG10",
    0x537E3563: "uEffectVFR::MyDTI",
    0x538120DE: "rSoundEngine",  # pc-only
    0x53822767: "tagWMVDecInternalMember",
    0x53851BB3: "cEm10ActDeadArmyBomb",  # pc-only
    0x538A61A6: "CXInviteSendMessage",
    0x5394DB85: "rCloth::Constraint::ConstraintType",
    0x53964E73: "CXLiveFriends",
    0x5398399D: "cOmCoopBoxActionPl",  # pc-only
    0x5399E7BD: "cEm84ActHang_Ready",  # pc-only
    0x5399F9AD: "NetworkSessionMcs",
    0x539C9AAA: "_DXVA_DeinterlaceQueryModeCaps",
    0x539F0F1F: "rEffect2D::E2D_UNIT",
    0x539F9D1D: "PatInterface::LayerComment",
    0x53A1A4B0: "uOmS109_Driver::cActDrive",  # pc-only
    0x53A2BD80: "D3D::NonSnoopedWriteBacks",
    0x53A43175: "DMIF_DEBUG04",
    0x53A5848E: "VC_PERFCOUNTER2_HI",
    0x53A97012: "AZ1_BC2AZ_CRC_READ",
    0x53ABA260: "tagWMCMarkerEntry",
    0x53B147A5: "uOm1307_Boat::cEventActDriving",  # pc-only
    0x53B4CC9E: "GC_MMR_BAR",
    0x53B536AB: "cPlAction_pl_act_jump_down",  # pc-only
    0x53B6AE30: "cEm41AActMissileRegene",  # pc-only
    0x53B838FB: "MPARAM_LINEARKEY",
    0x53BDFCE0: "EFC_PARAM_U8_DUAL",
    0x53C1BF4D: "CP_ME_PS_EVENT_ADDR_SWM",
    0x53C4C740: "DC_LUT_30_COLOR",
    0x53C7F139: "_XIPTV_DVR_QUERY_STATUS_MSG_ARGS",
    0x53CEC6FE: "cOmWindowAction_dummy",  # pc-only
    0x53D12C99: "uEffectVFR::LifeFrame",
    0x53D18B6F: "cTrans::CMD_SHADERGPR",
    0x53D455F0: "_IMAGE_CE_RUNTIME_FUNCTION_ENTRY",
    0x53DAB4B1: "_XALLOC_PRIVATE_ALLOCATOR_IDS",
    0x53DF9ADA: "cEm10ActHangWall",  # pc-only
    0x53E0DC41: "PCIE_ORDER_COMPLIANCE",
    0x53E233F3: "_PAT_MSG_DEF",
    0x53E26270: "cPositionEvaluationDistToPos",  # pc-only
    0x53E6FAB8: "XAUDIO::CPhysicalMemoryManager",
    0x53EBA31A: "TCB_TAG1_DEBUG",
    0x53EBE340: "IXHVEngine",
    0x53F02E55: "uEffectVFR::GridNorm::__vftable",
    0x53F155D9: "sBenchmark::BenchmarkInfo",  # pc-only
    0x53F17D7B: "AZ0_MRU_BANK4_DEPTH_MASK",
    0x53F3F611: "TCF_PERFCOUNTER0_LOW",
    0x53F4347A: "_XSHOWQUICKCHATUI_PARAMS",
    0x53F487E5: "CACHE_LINE",
    0x53F5C180: "MtSphere",
    0x53F8B875: "IUnknown",
    0x53F9C67D: "NetworkSocketXbox",
    0x53FA3E8F: "TP2_CNTL_STATUS",
    0x53FA3F4B: "_D3DXBONECOMBINATION",
    0x53FD81CE: "_XCONTENT_REFERRAL_RESPONSE",
    0x53FDAD39: "VC_DEBUG_REG3",
    0x53FF900D: "cEm82DmgLastPinionEnd_PL",  # pc-only
    0x54015428: "cOmCartridgeAction_om_act_wait",  # pc-only
    0x5401C0BC: "RTS_J_W_DX",
    0x5407F1B7: "cEmA2ActSyutoDie_PL",  # pc-only
    0x540AF831: "_CERTIFICATE_REVOCATION_LIST_HEADER",
    0x540C0687: "uCapLogo",  # pc-only
    0x540D2D92: "cEm34ActMotion",  # pc-only
    0x540F98B2: "_DRCData",
    0x54123366: "_FB_SUBMIT_COMPLAINT_REQUEST",
    0x541602B4: "GPUCmdFrameDone",
    0x541802E3: "FSB_TLA_COUNT2_INIT",
    0x541BA228: "uOmClutch::cActBase",  # pc-only
    0x542434FC: "rCloth::Constraint",
    0x5430EFB5: "cEm65ActWait",  # pc-only
    0x5431E8B1: "_P_CANCEL_MSG_INTERNAL",
    0x54388964: "TP1_PERFCOUNTER0_SELECT",
    0x5438B0F3: "VGT_DEBUG_REG8",
    0x543DF174: "D1SCL_HORZ_FILTER_CONTROL",
    0x5445F78F: "uOmExplosive::cActExplode",  # pc-only
    0x5447E3C0: "CP_DEFAULT_PITCH_OFFSET",
    0x544A5981: "uActorModel::EffectEmitter::DIR_TYPE",
    0x544AA3DC: "cEm20ActDieBomb",  # pc-only
    0x544BD923: "_SUB_Q_MEDIA_CATALOG_NUMBER",
    0x544E8164: "_FB_PLAYER_REVIEW",
    0x54569670: "COHER_DEST_BASE_6",
    0x545AB6C6: "_DXVA_COPPSetProtectionLevelCmdData",
    0x545B13A5: "CCalImagePlayer::ImageState",
    0x54604547: "cEm10ActCatch",  # pc-only
    0x54627A58: "cOmBoatAirAction_pl_act_change",  # pc-only
    0x546A9E1D: "XDVO_DEBUG1",
    0x54712490: "IXAudioSubmixVoice",
    0x5472223B: "ED_CHIP_ID",
    0x5473392C: "_FXLANNOTATION_DESC",
    0x54740725: "FSB_TLA_STATE_CONTROL",
    0x5476E759: "NetworkSessionManagerPat::Binary",
    0x5476FF33: "_XMUBYTEN4",
    0x54776EEF: "cEm40ActFarCatch",  # pc-only
    0x547BB351: "cEm42CActRegene",  # pc-only
    0x547C4C75: "cFSMOrder::FuncParamAreaHit",  # pc-only
    0x547CCBDD: "XUINotifyHtmlLinkHovering",
    0x5480772E: "_FIND_USER_INFO",
    0x54830E66: "MtCollada::Library",
    0x54866464: "cEm6fActErase",  # pc-only
    0x54868E09: "CP1_INT_VECTOR",
    0x5487FEBA: "uImagePlaneFilter::MyDTI",
    0x548C36E5: "PA_CL_UCP_2_X",
    0x548D075D: "XUIMessageGetHtmlReplacementImage",
    0x54906920: "VC_DEBUG_REG7",
    0x5490B7C7: "uEffectEdit::Line",
    0x549C914F: "_XHTTP_REQUEST_DOWNLOAD_TO_CACHE_PARAMS",
    0x549DDA04: "STREAMSTATUS",
    0x549E9071: "cPlAction_pl_act_avoid_front",  # pc-only
    0x549F95C0: "cNetEm32",  # pc-only
    0x54A12F70: "cEm10ActDeadErase",  # pc-only
    0x54A1C553: "cScenarioArg_BootFSM",  # pc-only
    0x54A47FFE: "uBackLight",
    0x54A56B81: "NQWAIT_UNTIL",
    0x54A5D075: "VecDecodeStatus",
    0x54A9C830: "_XUSER_STATS_SPEC",
    0x54A9C99C: "uScrModel",  # pc-only
    0x54ABA290: "cEm83PlEvent_Catch",  # pc-only
    0x54ACF1FC: "_DRIVER_OBJECT",
    0x54B3F68D: "cEm34ActFall",  # pc-only
    0x54B47BC6: "_PURCHASE_OFFER_PRICE",
    0x54B4C7C7: "DCP_DEBUG_ID",
    0x54B74AD3: "cPlAction_pl_act_damage_ice",  # pc-only
    0x54B92BDC: "MaskResampleInfo",
    0x54BEE478: "TP3_CHICKEN",
    0x54C25CD9: "AZ1_ACC_MASK",
    0x54C804A0: "MtCollada::Asset",
    0x54C86EA9: "cItAction_it_act_gain",  # pc-only
    0x54C96585: "XAUDIO::CEngine",
    0x54C9F56C: "DMIF_DEBUG00",
    0x54CAB763: "rEffectList::GENERATOR_OPTION_FLAG",
    0x54CC196D: "uEffectEdit::Model",
    0x54CF93CE: "VC_PERFCOUNTER0_LOW",
    0x54D350FD: "GPULOADTYPE",
    0x54D542AF: "D1CRTC_OVERSCAN_TOP",
    0x54D95E9C: "uEffectVFR::POLYGON_VERTEX_INDEX_TYPE",
    0x54DA1CED: "sApp::Item::GROUP",
    0x54DDDFA8: "sCapture::MyDTI",
    0x54E10547: "RBBM_PERFCOUNT1_SEL",
    0x54E53A5F: "cFSMOrderPawn::FuncParamSetAction",  # pc-only
    0x54E6A16B: "uBloomFilter",
    0x54EED327: "uOmLaserMirror::cActTurn",  # pc-only
    0x54F02A60: "cPlAction_pl_act_attack_sakotu",  # pc-only
    0x54F69F43: "D1CRTC_H_SYNC_A_CNTL",
    0x54FA27D1: "CP_RT11_BADR",
    0x54FC9C8E: "FSB_LX_LERST_OR",
    0x54FD54B6: "uOmTreasureBox::cActWait",  # pc-only
    0x54FE2775: "uOm0201_Piano::cActPiano",  # pc-only
    0x54FE2FF3: "_RC4_HMAC_HEADER",
    0x55015884: "CCalVideoInfo",
    0x55021E3A: "StereoMode",
    0x550511EB: "_D3DZBUFFERTYPE",
    0x55066BD9: "GPUPERFEVENT_PA_SC",
    0x550855CF: "cOmCoopTwistAction",  # pc-only
    0x551B3A59: "_D3DMATRIX",
    0x5523CB38: "cEm80ActSyutoRevEnd_PL",  # pc-only
    0x552BA9C7: "cOmRider2ActDmgL",  # pc-only
    0x5530670C: "HMONITOR__",
    0x5537948A: "cOmDoorActDead",  # pc-only
    0x553B20E6: "_XSHOWMARKETPLACEUI_PRIVATE_ENTRYPOINTS",
    0x554489D1: "MtXmlReader::PARSE_STATE",
    0x5545B5D4: "_D3DXWELDEPSILONS",
    0x5549F347: "cWpAction_act_knife_hand_rev",  # pc-only
    0x554AB022: "MtPreProcessor::REPLACE_MODE",
    0x554AE1F1: "formpeak",
    0x554D3296: "tagBITMAPINFOHEADER_WMC",
    0x554E5CD2: "PA_CL_UCP_3_X",
    0x555905B7: "uOmS109_Driver::cActDead",  # pc-only
    0x555936F1: "_DXVA_Status_H264",
    0x55626E97: "PCIE_P_PAD_FORCE_EN",
    0x55663964: "BIOS_14_SCRATCH",
    0x55667C5E: "AZ1_LOOPBACK_PATTERN1PHS0",
    0x55700F70: "CODECMSGINFO_RESETRENDERER",
    0x55755F3F: "RB_SAMPLE_COUNT_CTL",
    0x5579F528: "rEffectSetData::ESD_SET_PRIM_MODEL",
    0x557B15BA: "sRender::CAPS",
    0x557BC1C1: "sSoundN::StreamVoice",
    0x557D28E3: "aS109::cActBarricadeBattleEnd",  # pc-only
    0x557ECC08: "rAHEffect",  # pc-only
    0x557FF004: "CCalDvdPlayer",
    0x5584DA96: "_XCONFIG_ALERTDATA",
    0x55869640: "cEm40ActNearCatch_PL",  # pc-only
    0x558DE50F: "cOmLadderAction_wait",  # pc-only
    0x55907BB2: "HHOOK__",
    0x5596193D: "std::_Unsecure_char_traits_tag",
    0x5599A109: "uOm095d_Stampede::cActFall",  # pc-only
    0x559F244C: "MtFile::FileInfo",
    0x55A07D96: "_RAW_DUMP_INFO",
    0x55A4931E: "_XHTTP_REQUEST_DOWNLOAD_TO_MEMORY_PARAMS",
    0x55A5ECD9: "sGpuParticle::TransHandler::__vftable",
    0x55AAFEDC: "SQ_INSTRUCTION_VFETCH_1",
    0x55ACC216: "_KDEVICE_QUEUE",
    0x55B0D18C: "_P_PEER_UNSUBSCRIBE_MSG",
    0x55BABD1F: "SQ_ACTIVITY_METER_CNTL",
    0x55BD2F30: "cEm0cActDmgBack",  # pc-only
    0x55BDE3C7: "_XGI_STATSREAD_MSG",
    0x55C22C8F: "PCIE_LC_STATE5",
    0x55C27DE4: "cEm80ActPinionEnd_PL",  # pc-only
    0x55C3F355: "uEffectEdit::MoveAdd",
    0x55C5AB92: "_DXVA_MBctrl_P_OffHostIDCT_1",
    0x55C61A13: "IXAudioRenderEffect",
    0x55C9B97A: "GPUINDEXTYPE",
    0x55CA70AC: "cOmLadderAction_base_actbtn",  # pc-only
    0x55CADA5E: "CP_RT_ME_RAM_RADDR",
    0x55D58746: "HRGN__",
    0x55D72343: "cPlAction_pl_act_attack_knee_bazooka_third",  # pc-only
    0x55E02F26: "uOmHourGlass::cActBreak",  # pc-only
    0x55E354BD: "sGpuParticle::FUNC_PRIM_TONEMAP",
    0x55E54B41: "cEm44ActDie",  # pc-only
    0x55E58D05: "_DXVA_MBctrl_H264",
    0x55E64B95: "cEm8cActJump",  # pc-only
    0x55E8B4BE: "XNetConfigStatus",
    0x55EE45F7: "cSetInfoOmCoopJumpBroad",  # pc-only
    0x55EF9710: "rHavokLinkCollisionLayout",  # pc-only
    0x55F011A4: "uEffectVFR::SPOT_LIGHT_WORK",
    0x55F21DB6: "cEm8cActDmgCore",  # pc-only
    0x55F24D20: "cEm80ActPinion_PL",  # pc-only
    0x55FD84A5: "XGI_SESSIONDETAILS_MSG",
    0x55FE2C75: "cEm32ActRun",  # pc-only
    0x55FE8544: "CP_RT9_POLL_ADDRESS",
    0x5610EFE5: "XAUDIOXMAFORMAT",
    0x5613398D: "sSoundN::DSPUnit",  # pc-only
    0x56151C31: "VGT_CNTL_STATUS",
    0x561AED9F: "cEm10ActDeadNormal",  # pc-only
    0x5622DB31: "OperandSelect0",
    0x5626F836: "uPlayer::ADD_OFS_JOINT_INFO",  # pc-only
    0x562828CF: "_XONLINECONTENT_RESUME_HEADER",
    0x56287C9C: "cSynchronization",
    0x56304984: "uOm0927_Crane::cActSwitchOn",  # pc-only
    0x5631D476: "_XCAB_STREAM_UNPACK_STATE",
    0x5636C915: "SB_STATUS",
    0x56384024: "std::_Lockit",
    0x5638678F: "_XGI_STATS_ENUMERATOR_TYPE",
    0x563F691C: "cEm80ActNeeNg_PL",  # pc-only
    0x564797C9: "cEm41CActVanish",  # pc-only
    0x5647A49E: "cEm30ActWait",  # pc-only
    0x564EA5FF: "GPUPERFEVENT_BC",
    0x5655FD6D: "cJointSymmetry",  # pc-only
    0x565AF0DF: "_IMAGE_NT_HEADERS",
    0x565B043D: "cEm20ActDmgCombo",  # pc-only
    0x565CDCAE: "tagWMA_MetaDataEntry",
    0x56622E8A: "cEm10ActAtkPlagaEat_PL",  # pc-only
    0x56656330: "cEm70ActTurn",  # pc-only
    0x5665791A: "cOmCoopBoxAction_om_act_dummy",  # pc-only
    0x566DA695: "ID3DXSPMesh",
    0x566F90FB: "MtRegistry::MyDTI",
    0x5676937E: "NetworkSessionManagerLive::moveJoinSession::__l3",
    0x5678894D: "TCF_PERFCOUNTER8_SELECT",
    0x56807625: "cEm10ActAtkThrowTrack",  # pc-only
    0x56819C32: "cEm84ActDmgBlowL",  # pc-only
    0x5682C5C9: "MtStream::MyDTI",
    0x5688234E: "PCIE_PORT_INDEX",
    0x5688BBF2: "cEmc3ActDownEnd2",  # pc-only
    0x568F376A: "uCascadeLSM::MyDTI",
    0x568F570B: "_FILE_STANDARD_INFORMATION",
    0x56929CF0: "cEm42SActWait",  # pc-only
    0x56949C3F: "sCollision::ScrColInfoBasic",
    0x5698D2B3: "GPUNUMFORMAT",
    0x569CECC8: "XAUDIOSOURCEFXFORMATPARAM",
    0x569D8AD8: "MC0_RD_BUFFER_CNTL_0",
    0x56A0FC68: "sockaddr",
    0x56A77157: "cEm40PActBlow",  # pc-only
    0x56A91B26: "D1CRTC_OVERSCAN_RIGHT",
    0x56AF65E6: "_CONTEXT",
    0x56B25FF1: "CCalMp3Decoder",
    0x56B37AB7: "FSB_LX_PHYCMD_OR",
    0x56B4B20C: "tagCWMVMBMode",
    0x56B77735: "MtCollada::BoundingBox::MyDTI",
    0x56CA88BC: "PA_CL_UCP_1_X",
    0x56CEBC34: "std::range_error",
    0x56CF09E0: "NetworkStoragePat",
    0x56CF0C17: "sNetworkLibrary",
    0x56D12F2B: "MP4TrackReaderRecord",
    0x56D20814: "PA_SU_CNTL_STATUS",
    0x56E5859F: "FSB_TLA_TRACEN_INIT",
    0x56E6F90E: "_SECURITY_ADVANCED_QUALITY_OF_SERVICE",
    0x56EAEFF8: "CXuiMultiApp",
    0x56F01E55: "DPFCONTEXT",
    0x56F5B156: "uModel::Motion",
    0x56F6C455: "_ACCOUNT_RESERVE_GAMERTAG_RESPONSE",
    0x56F82FDB: "NetworkLayer::Id",
    0x56FB30FA: "AZ0_MRU_BANK8_DEPTH_MASK",
    0x57000965: "_D3DSWAPDATA",
    0x5704BE58: "HSIO_DLL_ADJ5",
    0x57076FCC: "_CLIENT_ID",
    0x57083BD6: "CP_RT3_SIZE",
    0x5708E28B: "PA_CL_UCP_0_X",
    0x5709B5C4: "GpuMocompInfo",
    0x570C44AE: "PIX_REQUEST_GET_DATA",
    0x57160932: "cEm83ActDmgSpecial",  # pc-only
    0x571AB398: "rModel::RCN_VERTEX",
    0x571CC730: "AZ0_LOOPBACK_PATTERN1PHS3",
    0x5720C11E: "VGT_PERFCOUNTER1_SELECT",
    0x5723084B: "uItemLight",  # pc-only
    0x57270A19: "rEffectSetData::MyDTI",
    0x572DFAF3: "MC1_DRAM_CONFIG",
    0x57393B57: "XVOICE_PACKET_CONTEXT",
    0x573BBAA7: "AZ1_COPY_STATE_DWORD2",
    0x573D3BF0: "D1GRPH_CONTROL",
    0x5742FE44: "uEm45::cActPlActStagger",  # pc-only
    0x57484E3D: "_PM4CMDSETSTATE",
    0x574B5778: "REVISION_ID",
    0x574F00FD: "rSoundSourceMusic::MyDTI",
    0x574FDCB6: "PatConnection::__vftable",
    0x57539315: "BC_DUMMY_CRAYRB_ENUMS",
    0x5759AC30: "MtVirtualAllocator",
    0x575AD4F1: "cLinkUnitNone",  # pc-only
    0x575D8CA3: "NCI_CODEC_INFO_BLOCK",
    0x57635794: "BSAFE_PUB_KEY",
    0x5765FDE8: "_FILE_COMPRESSION_INFORMATION",
    0x5766D9C6: "GPUCLAMP",
    0x5771F580: "PatInterface::LayerName",
    0x577486B7: "XGI_SESSIONINVITE_MSG",
    0x57769AB0: "uToneMapFilter::STAR_TYPE",
    0x577A1B23: "D3D::HangRegister",
    0x577DD473: "cEm44ActDown",  # pc-only
    0x5780B576: "CP5_INT_VECTOR",
    0x5781C6E7: "CDXVAWMV",
    0x5787D7AE: "uOma00f_UroPunch::cActPunch",  # pc-only
    0x57895BBC: "uEffectVFR::Line",
    0x578AB35A: "CXrlConnection",
    0x578E2D23: "PCIE_P_IMP_CNTL_STRENGTH",
    0x578E4689: "GPUEDRAMCOLORFORMAT",
    0x578F5DC5: "FSB_TLA_CONDITION0",
    0x57954DE9: "XAUDIOPERFCOUNTER",
    0x57994D6D: "MtCollada::Instance::MyDTI",
    0x579AD874: "uOm1316_BackupHeli::cEvActBase",  # pc-only
    0x579DA233: "_UCODE_R500PSUCODE",
    0x579E9A02: "tagWMAExtendedContentDescription",
    0x57A60A5C: "XDVO_ENABLE",
    0x57B2F66B: "EFC_CULLING",
    0x57B77761: "uToneCurveFilter",
    0x57BC3DFB: "_LSP_ENUMERATE_REQUEST",
    0x57BCF94C: "uOm1303_S109_Truck::cActBarricadeBreak",  # pc-only
    0x57C2AC85: "uModel::Joint::ATTRIBUTE",
    0x57CD718D: "_D3DRESOLVE_PARAMETERS",
    0x57CEC043: "XAUDIO::CSourceStream::__vftable",
    0x57CF179F: "cPlAction_pl_act_damage_egg",  # pc-only
    0x57D3EF50: "CXMessageDownloadAttachmentToMemory",
    0x57D4840C: "cPlAction_pl_act_attack_straight",  # pc-only
    0x57D8F5D8: "cEm10ActDmgLadder",  # pc-only
    0x57D9E577: "uEffectEdit::TexlineKeyframe",
    0x57DE8A03: "CP_RT_DMA_DST_ADDR",
    0x57E047F5: "std::random_access_iterator_tag",
    0x57EA0D1A: "MPARAM_QUATERNION3",
    0x57EA2615: "uOmS508_Break::cActBase",  # pc-only
    0x57EE05D4: "cEm30ActNeckBiteHitTH",  # pc-only
    0x57F3ECA0: "uOmSwitchPulley::cActPulleyWaitToGo",  # pc-only
    0x57F3FE65: "CHARTYPE",
    0x57F449C7: "tQWORD_WMC",
    0x57F4572C: "uEffectEdit::RELATION_END_TYPE",
    0x57FA189D: "MtCollada::Channel",
    0x5802B3FF: "rAHCamera",  # pc-only
    0x5803E1E7: "sCollision::UPDATE_SPD_ADJPOS_RET_ID",
    0x5805D69A: "cEm63ActDmg",  # pc-only
    0x580D57C1: "CXaudioPixAutoEvent",
    0x58160A2F: "uMovie::PRESENTATION_MODE",
    0x581F2EAE: "BIOS_1_SCRATCH",
    0x581F7862: "CRTC1_DEBUG_06",
    0x5821B7F6: "cHitUniqueID",  # pc-only
    0x58236DC3: "_complex",
    0x5824227B: "tagGPUCmd",
    0x582D5A03: "_P_FIND_USER_MSG_INTERNAL",
    0x582F0068: "DCCG_ONE_SHOT_CLOCKING_CNTL",
    0x58346C08: "_DVD_XGD2_DISC_AUTH_RESULT_LBA_IO_ERROR",
    0x58350DAA: "CCalHttpStream",
    0x5837DDAD: "GPUTESSMODE",
    0x583C61E1: "CXuiAnimRunner",
    0x583FE225: "rObjAdjXml",  # pc-only
    0x584279B3: "_SVOD_HASH_ENTRY",
    0x58462391: "MP4InputStreamRecord",
    0x584652A5: "rSoundStreamRequest::SOUND_STREAM_READ_TYPE",
    0x58497C7A: "_KEVENT",
    0x584CEC0D: "_CERTINIT",
    0x58523468: "cPlAction_pl_act_ladder_v_climb",  # pc-only
    0x58529AAC: "_DXVA_MBctrl_P_HostResidDiff_1",
    0x58529CDC: "_P_GET_FRIENDS_LIST_REPLY_DATA",
    0x5852C3F9: "_XEKEYS_SET_REVOCATION_LIST",
    0x5856E50C: "MtCollision::LocalBlockAllocator::BlockInfo",
    0x585831AA: "rPos",  # pc-only
    0x5859F31C: "CWMAInputBitStream",
    0x585A0E8C: "cEm10ActAtkThrow",  # pc-only
    0x585A3FA7: "tagPanSscanInfo",
    0x585EB32F: "_XGMICROCODESHADERPARTS",
    0x585EED7E: "_DXVA_Highlight",
    0x5864BC9C: "PMD",
    0x58660A4D: "_ACCOUNT_SUGGESTED_GAMERTAG",
    0x5868990C: "cEm10ActAtkPlagaV",  # pc-only
    0x586CD927: "_IMAGE_THUNK_DATA64",
    0x586F8457: "FSB_LX_DADD_AND",
    0x5870CCF2: "_XPROFILE_ENUM_TITLES_REQUEST",
    0x58737B6B: "_XONLINE_STATS_ROW",
    0x5875A0C6: "_FILE_FS_CONTROL_INFORMATION",
    0x5878413C: "CCalBase::AV_SYNC_STATUS",
    0x58806D95: "XPLAYERLIST_BUTTON",
    0x5884116E: "uOmPlate::cActBase",  # pc-only
    0x5885456F: "CCalMovieDecoder::__vftable",
    0x588DE5AC: "FrameInfo",
    0x589063E9: "VIDEORENDERINGSETTINGS",
    0x5892F393: "cOmContainerAction_dummy",  # pc-only
    0x5893FFA6: "_ldiv_t",
    0x58963EA1: "cEm66ActAtkRaftBiteHit",  # pc-only
    0x589BD8D4: "uOmSwitch3::cActWait",  # pc-only
    0x589F3601: "rEffectSetData::ESD_SET_CHAIN_POLYLINE",
    0x58A15856: "rModel",
    0x58ADF632: "D3D::FixupType",
    0x58AE2E55: "cPlAction_pl_act_item_hand_partner_second",  # pc-only
    0x58B26488: "rEffect2D::MOVE_TYPE",
    0x58B297FE: "PA_SC_SCREEN_SCISSOR_TL",
    0x58C03E7E: "_P_TEAM_LIST_TEAMS_MSG",
    0x58C0EC3B: "_RTL_HEAP_WALK_ENTRY",
    0x58C26ADB: "AHShapeSphere",  # pc-only
    0x58C303DA: "PatInterface::LayerNameList",
    0x58C6E7EB: "cPlAction_pl_act_item_use_my_first",  # pc-only
    0x58C72E3D: "sApp::Item",
    0x58C8E0C1: "DC_LUT_WRITE_EN_MASK",
    0x58CD014D: "uModel::Constraint::MyDTI",
    0x58D4100C: "cPositionFilterDoughnutAroundPlayerPos",  # pc-only
    0x58D6C399: "XMSG_OP_TYPE",
    0x58D9E020: "GPUEXPORTREGISTER_PS",
    0x58DA8238: "cHavokVehicle",  # pc-only
    0x58DC5D46: "_BANNER_LIST_ENTRY",
    0x58DDE447: "uEffectEdit::PTCL_STATUS",
    0x58E09A7E: "MtSerializer::MODE",
    0x58E2B0B4: "IXAudioBatchAllocator::__vftable",
    0x58E69739: "cEm41CActMotOnce",  # pc-only
    0x58E75213: "STREAMINFO",
    0x58E96E56: "D3D::WriteBacks",
    0x58EEBC32: "ID3DXLoadUserData",
    0x58F1D822: "cTrans::VertexBuffer",
    0x58F6C215: "GPUTEXTUREFORMAT",
    0x58FC7EDA: "_DIRECT_DEBIT_INFO",
    0x58FE68C4: "uEffect2D::PTCL_LIFE_RNO_TBL",
    0x58FF4633: "_PixFacility",
    0x59044160: "_XAMUSER_SIGNIN_STATE",
    0x59047FB7: "CP_DEFAULT2_SC_BOTTOM_RIGHT",
    0x59084DB1: "FSB_LX_DDAT1",
    0x59089D77: "cEm10ActAtkDashStunRod",  # pc-only
    0x59097F3F: "uEffectEdit::STRIP_WORK",
    0x590ABDBC: "cPlAction_pl_act_ready_wait_front",  # pc-only
    0x590DC121: "tagPlannedOutputId_WMC",
    0x590DF82F: "uSpotShadow::MyDTI",
    0x590E833C: "cEmc0ActFinish_Pl",  # pc-only
    0x5917F84B: "NetworkSingleTcp::__vftable",
    0x5918769F: "cJeepSub",  # pc-only
    0x591F5239: "ID3DXAllocateHierarchy",
    0x592278B5: "_tag_AMVABUFFERINFO",
    0x59248909: "HMETAFILE__",
    0x592B6DEF: "uEffectVFR::ClothCurve",
    0x592C12D4: "uOm0892_Lift::cActPlBase",  # pc-only
    0x592D804B: "rSoundCurveXml",
    0x592D9804: "rVibration::VIB_HEADER",
    0x5931F210: "cOmRider2ActDeadErase",  # pc-only
    0x5932BBDC: "VGT_DMA_REQ_FIFO_DEPTH",
    0x5932EEB2: "XPLAYERLIST_BUTTON_TYPE",
    0x5933AE22: "CP_RT0_MASK",
    0x59345049: "cPlAction_pl_act_damage_sulfate",  # pc-only
    0x59351470: "uToneMapControl",
    0x593524DB: "IOC_INVALID_AP_DATA",
    0x5935638B: "cEm10ActJumpDown",  # pc-only
    0x593A564E: "PCIE_P_BUF_STATUS",
    0x593D098A: "rEffect2D::E2D_PARAM_DRAW",
    0x59409C6A: "rAIFSM::ParamSubCondition",  # pc-only
    0x5945BE24: "ID3DXFileSaveData",
    0x5948DA6F: "MC1_POINTER",
    0x594B390E: "CP_CMD_DATA",
    0x594D31D6: "GpuFilterWaveEntry",
    0x5952380D: "uOm08e9_S303Elev::cActWaitFall",  # pc-only
    0x59543AD0: "FSB_TX_CMDMM0_OR",
    0x5959C60D: "rEffectSetData::PRIM_MODEL_AXIS_TYPE",
    0x595ADE2F: "GPUPATHSELECT",
    0x595C5B5E: "Abs_modifier",
    0x5960CD5C: "_D3DGAMMARAMP",
    0x59652D27: "cNetEm80",  # pc-only
    0x596E079D: "PREF_BASE_LIMIT",
    0x59734EF2: "cEm40ActDive",  # pc-only
    0x5977D85B: "NetworkLayer::Server",
    0x5979F211: "_COPYSTATE",
    0x597CDBB7: "rShapeWeight::WEIGHT_HDR",
    0x597CE8E5: "sPhysics::RigidBody",
    0x5981388A: "CXLiveSubTask",
    0x5982031D: "uInfiniteLight",
    0x5989C70D: "MtCollada::Skin",
    0x598D77BD: "IXMediaXmvPlayer",
    0x598ED848: "SCHEMA_CONFORMING_INFO",
    0x5993C840: "LB_DISP1_ALU_PARAM",
    0x59A12BE7: "cPlAction_pl_act_attack_upper_em10",  # pc-only
    0x59A3A6EF: "AZ0_LOOPBACK_AZID",
    0x59A455B2: "uOmS508_Break::cActDisappear",  # pc-only
    0x59A69BF2: "GPUEXECSERIALIZEMODE",
    0x59A78608: "_ACL_REVISION_INFORMATION",
    0x59A8C161: "uOm08b8_Limited::cActLeave",  # pc-only
    0x59A8C4DF: "rSoundSourceXMA::MyDTI",
    0x59ADBA18: "D3D::XBMCAPTURETYPE",
    0x59AFC6FD: "VGT_PERFCOUNTER2_SELECT",
    0x59B857B7: "uOmExplosive::cActBase",  # pc-only
    0x59B87D35: "cEm80ActKataWait_PL",  # pc-only
    0x59BEBA36: "DISP_INTERRUPT_STATUS",
    0x59C83238: "VGT_GROUP_VECT_0_CNTL",
    0x59C9F138: "_XINPUT_KEYSTROKE",
    0x59D0943C: "XUIMessageScroll",
    0x59D42E72: "EffectLog",  # pc-only
    0x59DEC68D: "sEventPlayer::entryPacket",  # pc-only
    0x59DFAD9A: "CP_RT_BASE",
    0x59E4DB67: "uIdBase",  # pc-only
    0x59E568E9: "_XPROFILE_CONTROLLER_VIBRATION_OPTIONS",
    0x59E60957: "MC1_RD_STR_DLY_CNTL",
    0x59E92BDE: "cEm40ActSunnySideUp",  # pc-only
    0x59EB6081: "_XGMIPTAIL_DESC",
    0x59EF9469: "_XAMTASKATTRIBUTES",
    0x59F8758E: "MtMath",
    0x59FA6557: "MP4TrackRunAtom",
    0x59FAA648: "PatInterface::UserObject",
    0x59FE4658: "CP_2D_PALETTE_BASE",
    0x5A02AB92: "_P_PRESENCE_2_ITEM",
    0x5A02D770: "cOmDoorActMiss",  # pc-only
    0x5A04675E: "_D3DXPATCHMESH",
    0x5A04CE96: "MtCollisionEpa::MtEpaLocalList::__vftable",
    0x5A0BAF54: "CXDirectoryCrawler::FILE_DIRECTORY_INFO_BUFFER",
    0x5A0D4C30: "uEffectVFR::PTCL_RNO_LINE_FIX_END",
    0x5A134EC8: "PRIOTITYREC",
    0x5A194709: "cEm84PlEvent_DownStrip",  # pc-only
    0x5A1DD78C: "D1MODE_URGENCY_STAT",
    0x5A1F22EB: "AZ0_LOOPBACK_TX_CRC_MASK",
    0x5A1F2CB3: "rEffectList::KEYFRAME_REF_TYPE",
    0x5A24B64C: "MtCollada::Geometry::MyDTI",
    0x5A25F18A: "rEffectList::EFL_PARTICLE_PRIM_MODEL",
    0x5A29107C: "PRESENCE_PROPERTY",
    0x5A2D96E4: "cEm20ActDieTrapCeil",  # pc-only
    0x5A2E584C: "sCollision::Sbc::Parts",
    0x5A34E69F: "NetworkPeer",
    0x5A4279D6: "sVibration",
    0x5A4BECB1: "cOmEventPL_ActPreNoMot",  # pc-only
    0x5A5246A8: "sId::Map",  # pc-only
    0x5A55BFBD: "_KD_GLOBAL_DATA_BLOCK",
    0x5A605A6B: "_SVOD_CREATE_PACKET",
    0x5A61B373: "CP_MEQ_THRESHOLDS",
    0x5A62EE8C: "sUnit",
    0x5A66E4BC: "cEm10ActAtkDashBothHand",  # pc-only
    0x5A66E79D: "_VD_NOTIFICATION_REGISTRATION",
    0x5A680D6B: "CP_CMD_INDEX",
    0x5A68C1FA: "sItem::ITEM_DROP_TBL",  # pc-only
    0x5A6B1F5E: "SCL1_LB_INTERFACE",
    0x5A6BCA0A: "tagAdjustDecRangeCtrl",
    0x5A72CDF6: "cEm30Action",  # pc-only
    0x5A761855: "AZ1_MRU_BANK9_DEPTH_MASK",
    0x5A7A511E: "DC_TEST_DEBUG_INDEX",
    0x5A80F24D: "_COPP_HDCP_Protection_Level",
    0x5A834563: "_STFC_FCB",
    0x5A85944F: "MC0_RDBUF_DATA",
    0x5A85BAA0: "CP_ME_RAM_DATA",
    0x5A85ECC2: "uModelEdge::MyDTI",
    0x5A89F657: "cEm41AActBreak",  # pc-only
    0x5A8D0CDE: "NetworkPeerParamLive",
    0x5A8D7B0E: "_XAM_CACHE_OPEN_FILE",
    0x5A8DC249: "aInit",  # pc-only
    0x5A94BD0B: "FSB_TLA_TRACE_ARRAY_AUX",
    0x5A974C04: "MC1_WR_STR_DLY",
    0x5A97D3DB: "cEm0cActDieFlash",  # pc-only
    0x5A9BD1FE: "XONLINE_CONTENT_HISTORY_ENUMERATE_FLAGS",
    0x5A9BD619: "D3D::LazyPrim",
    0x5A9BE3D3: "cPlAction_pl_act_item_get_use_first",  # pc-only
    0x5A9D3DA0: "cEm83ActWait",  # pc-only
    0x5AA16A59: "GPUDESTBASE7",
    0x5AAE4E7C: "_XSTORAGE_ENUMERATE_RESULTS",
    0x5AAF3B77: "uOmLaserMirror::cActCatch",  # pc-only
    0x5AAF9D69: "cEm0cActRelease",  # pc-only
    0x5AB1DF34: "uModel::DEBUG_FLAG",
    0x5ABA9373: "IOC_BSB_MST_REQ_CRC_1",
    0x5AC010E5: "uCaption",  # pc-only
    0x5AC18E2F: "IXAudioEffect::__vftable",
    0x5ACC277F: "CCalWmvDecoder",
    0x5ACF9771: "TypefaceDescriptor",
    0x5AD30A9C: "cFSMOrder::FuncParamBenchCamera",  # pc-only
    0x5ADEAAB3: "MP4List",
    0x5ADF134B: "_LOGON_CHECK_RESPONSE",
    0x5AE0A295: "_ENUMERATE_TITLES_BY_FILTER_REQUEST",
    0x5AE29D0F: "stdext::bad_exception",
    0x5AE338C1: "VGT_DEBUG_REG0",
    0x5AE9FC44: "MtPreProcessor::MACROTABLE",
    0x5AECF0BB: "sCollision::PreTraverseInfo",
    0x5AED6145: "AZ0_PRIMARY_STATE_DWORD0",
    0x5AEE7F0A: "TP3_DEBUG",
    0x5AF0348C: "MtDefaultAllocator",
    0x5AF26EF1: "INPUTSRCBUFFER",
    0x5AF4E4FE: "rMotion",
    0x5AFAADED: "PIX_FRAME_DIFF",
    0x5AFC1E6E: "CRWLock",
    0x5AFE5674: "uBgmCtrl",  # pc-only
    0x5AFF2A61: "FSB_TX_DEBUG_AUX_AND",
    0x5B05134F: "FSB_LX_PHYDATA_AND",
    0x5B07A68C: "_P_GET_PEER_SESSION",
    0x5B0B16F2: "AZ0_ZPASS_SAMPLES",
    0x5B0F772F: "cPlAction_pl_act_attack_combo_reverse_knuckle",  # pc-only
    0x5B109907: "cFSMOrder::FuncParamMessage",  # pc-only
    0x5B125152: "VGT_PERFCOUNTER2_HI",
    0x5B1318C2: "MC1_DRAM_DQ",
    0x5B13B7B0: "cTrans::TextureBase",
    0x5B1C2F02: "cOma016ActCut03",  # pc-only
    0x5B224B0F: "D1GRPH_X_START",
    0x5B22BAE4: "VGT_PERFCOUNTER0_LOW",
    0x5B245B64: "MC0_STATUS_1",
    0x5B26FDD5: "SQ_CONSTANT_RT_3",
    0x5B339386: "CP_ME_CF_EVENT_SRC",
    0x5B358AC3: "CXStorageUploadFromMemory",
    0x5B3864DA: "D1MODE_MASTER_UPDATE_LOCK",
    0x5B3A2A19: "MtGeomPlane",
    0x5B3A60E1: "cEma2ActHumituke_Kaihi_PL",  # pc-only
    0x5B3ADE30: "_STF_HASH_ENTRY",
    0x5B417D7F: "CCalReadAheadFileStream::__vftable",
    0x5B42B9CB: "_P_INVITE_2_MSG_INTERNAL",
    0x5B42CB96: "AreaHitShape",  # pc-only
    0x5B42D39D: "_D3DXEVENT_TYPE",
    0x5B452855: "_COPP_CGMSA_Protection_Level",
    0x5B466EDF: "uAdhesion::FUNC_ADHESION_ALPHA_TYPE",
    0x5B47A84C: "_XONLINE_THROUGHPUT_STATS",
    0x5B4CD880: "cShape::transBlend::__l10::MAP_VERTEX",
    0x5B4E85E5: "sPhysics::RigidBody::__vftable",
    0x5B4EFF70: "uOm1303_Truck::cActMain",  # pc-only
    0x5B4F3411: "cEm84PlEvent_Strip",  # pc-only
    0x5B501C07: "D3DPerfCounters",
    0x5B547A9E: "rEffectList::CLOTH_TYPE",
    0x5B559B25: "cPlAction_pl_act_avoid_crouch_in",  # pc-only
    0x5B5B9121: "RBBM_READ_ERROR",
    0x5B5DC6E3: "cEm22ActDieIce",  # pc-only
    0x5B60B147: "_XMSG_SEND_PARAMS",
    0x5B634146: "cPlAction_pl_act_weapon_change_ready",  # pc-only
    0x5B6A0589: "NetworkMediator::__vftable",
    0x5B6E28F7: "rAIFSM::Transition",  # pc-only
    0x5B71196D: "TCM_PERFCOUNTER0_SELECT",
    0x5B756274: "CP_RT14_POLL_ADDRESS",
    0x5B774F77: "_TypeDescriptor",
    0x5B791319: "C_BUFFER_TYPE",
    0x5B7B9353: "cEm6fActDieIce",  # pc-only
    0x5B7DA4AA: "cFSMOrderEnemy::FuncParamSetEmAttr",  # pc-only
    0x5B7F31DF: "uOmS104_Driver::cActCrash",  # pc-only
    0x5B7F83D9: "_XNCALLER_TYPE",
    0x5B81B9EF: "ColorFormat",
    0x5B839C27: "MtCollision::PenetrationDepthSimplexSolver",
    0x5B8991C7: "cEm84ActDmgBlowS",  # pc-only
    0x5B8CB896: "PCIE_VC0_STATUS",
    0x5B8D71C4: "XGI_SYNC_MSG",
    0x5B9226AD: "cEm44ActAtckArm",  # pc-only
    0x5BA403C9: "_DXVA_ProcAmpControlQueryRange",
    0x5BA7E7A9: "MtDTI",
    0x5BAA6F0F: "NetworkLayer::PropertyList",
    0x5BADC52F: "MtCollada::Accessor",
    0x5BAF968E: "CP_CSQ_RB_STAT",
    0x5BB30D6B: "PA_SC_PERFCOUNTER3_HI",
    0x5BBF6D46: "REG_MACRO_DATA_7",
    0x5BC31412: "MP4CompositionOffsetAtom",
    0x5BC388A3: "_ERWLOCK",
    0x5BC443CD: "MtMemoryStream",
    0x5BC66843: "rHkRBInfoList::rbInfo",  # pc-only
    0x5BC87AB4: "AHCameraArea",  # pc-only
    0x5BC9841F: "DMPSDATA",
    0x5BCC2D05: "BIU_INT_UNKNOWN_CMD_VALUE",
    0x5BCFB51A: "cOmCoopBoxAction_om_act_down_break",  # pc-only
    0x5BD2F463: "SB_CAPABILITIES_PTR",
    0x5BD52EF5: "XUICharMetrics",
    0x5BDD4FF2: "XUIMessagePress",
    0x5BDD7F3B: "uCloth::Chain",
    0x5BE4F884: "uOmSwitch3::cActMid2Push",  # pc-only
    0x5BE9B0BC: "PCIE_LC_TRAINING_CNTL",
    0x5BEE15B9: "_XNET_LOGON_CUSTOM_SERVICE_ID_LIST",
    0x5BF77483: "cLinkUnit::cTargetObjModel",  # pc-only
    0x5BFD0008: "TOP_OF_MEMORY",
    0x5C018205: "_MP_BILLING_ACCOUNT_INFO",
    0x5C0809AB: "XDVO_CRC_EN",
    0x5C0911D5: "XAUDIO::XAUDIOVOICEINIT",
    0x5C0BB481: "CUnmarshaller",
    0x5C0C0656: "D1OVL_END",
    0x5C0C5D28: "_D3DXMESHOPT",
    0x5C0F0391: "MtClipboardStream::MODE",
    0x5C103430: "_audecState",
    0x5C10BE5A: "XG_MCT::MNode",
    0x5C1117BD: "_XMSG_DETAILS_GET_PROPERTY",
    0x5C18E2F0: "princeton_digital::threetap_t",
    0x5C24F307: "DCACPREDDIR",
    0x5C2928E0: "_D3DXEVENT_DESC",
    0x5C294444: "_STFC_ALLOCATE_BLOCK_STATE",
    0x5C2B3EDA: "_ImageArchitectureHeader",
    0x5C2C94CA: "_XONLINE_STATS_VIEW",
    0x5C2CE625: "cEm10ActWalkGuard",  # pc-only
    0x5C2D5CEA: "cTrans::CONTEXT",
    0x5C2E7B91: "PCIE_TX_CREDITS_LIMIT_D",
    0x5C355707: "uOm08e3_RuinTrap::cActTrap",  # pc-only
    0x5C3763E0: "cFSMOrderElevator::FuncParamElevatorCamera",  # pc-only
    0x5C37D13E: "_XONLINE_ATTRIBUTE_BLOB",
    0x5C395700: "D3DConstantBuffer",
    0x5C3B1F23: "sEffectBase::MyDTI",
    0x5C3E96AB: "rEffect2D::RT_NM_CONVERT",
    0x5C3F30D0: "rSoundSourceXMA",
    0x5C4100FD: "CMpegHeader::__vftable",
    0x5C42EA35: "_USER_ACCOUNT_INFO",
    0x5C48E4CB: "aS109::cActBarricadeBattleStart",  # pc-only
    0x5C48FBEF: "XAUDIO::XAUDIOFXNUMERICPARAMCTX",
    0x5C4B4596: "MtCollada::Input::MyDTI",
    0x5C4D7A1A: "MtFCurve::Key",
    0x5C513FC8: "sEffect::RadialBlurFilterControl",
    0x5C5795E9: "cEm42TActWait",  # pc-only
    0x5C57E929: "DCCG_DEBUG_03",
    0x5C59D6B6: "CCalVideoDecoder::__vftable",
    0x5C620D3A: "NetworkRanking::ScoreList",
    0x5C621ACF: "uOm0912_s119Tram::cActPlJump",  # pc-only
    0x5C6A972B: "rEffectList::INP_TYPE",
    0x5C6FCFE1: "_DEVICE_NOTIFICATION",
    0x5C70FCED: "sPhysics::cPhysicsBaseObject::MyDTI",
    0x5C73C892: "uNoiseFogFilter::MyDTI",
    0x5C7A6EAB: "AZ1_MRU_BANK1_DEPTH_MASK",
    0x5C7E9717: "strAudioStreamInfo_WMC",
    0x5C8084AF: "TCR_PERFCOUNTER0_SELECT",
    0x5C816CB4: "MC0_SECURE_MEMORY_APERTURE_BASE",
    0x5C8273C8: "PCIE_PERF_COUNT1_SLV_NS_C_CLK",
    0x5C827B98: "sCamera::MyDTI",
    0x5C865C26: "_POINTL",
    0x5C89093E: "_XSTORAGE_PATH_STRING",
    0x5C9B5449: "D3DIndexBuffer",
    0x5C9C259A: "std::ostreambuf_iterator",
    0x5C9C401E: "cDemoWaitSignOut",  # pc-only
    0x5CA71792: "PCIE_RX_TLP_HDR3",
    0x5CB045D8: "cOmBoatAirAction_om_act_change",  # pc-only
    0x5CB134E8: "XUIMessageTopLine",
    0x5CB1782E: "NetworkCommunity::FriendList",
    0x5CB303B1: "TCF_PERFCOUNTER6_LOW",
    0x5CB463D8: "uEffectEdit::Polygon",
    0x5CB78360: "_D3DFILTER_PARAMETERS",
    0x5CB7DC6B: "cOmBoatAirAction_pl_act_ride_off",  # pc-only
    0x5CB82383: "rEffect2D::RANGE_TYPE",
    0x5CB86417: "MtOBB",
    0x5CB9D1D2: "rEffectList::RELATION_TYPE",
    0x5CBAB342: "rSoundSourceEnvironment",
    0x5CBD9CB9: "CP_PROG_COUNTER",
    0x5CBEB862: "SBR_ELEMENT_ID",
    0x5CBFF7E6: "XAUDIO::XAUDIOSRCDEST",
    0x5CC71D20: "cEm42CActDeathBeatOk",  # pc-only
    0x5CC94315: "rTexture::HEADER",
    0x5CCD5A57: "XUIMessage",
    0x5CCEEB22: "uOm08b3_S203Elev::cActWaitOpen",  # pc-only
    0x5CD05D18: "SQ_CONSTANT_1",
    0x5CD15CA2: "FSB_TLA_PATT_CARE_MASK0",
    0x5CD23807: "MtXmlReader::ENCODE_TYPE",
    0x5CD2A95F: "REG_MACRO_DATA_3",
    0x5CD2B3FC: "_GET_POSTAL_CODE_RESPONSE",
    0x5CD6A30C: "_XCONTENT_DOWNLOAD_PARAMS",
    0x5CD95CA6: "cEm41AActMissile",  # pc-only
    0x5CDD1F19: "cResource",
    0x5CEA8417: "cEm45ActPlagaWait",  # pc-only
    0x5CEBCE40: "cEm66ActAtkSwimBite",  # pc-only
    0x5CECEBB6: "rSoundMotionSe::cSoundMotionSeData",  # pc-only
    0x5CF2E134: "_XMSG_ENUMERATE_REQUEST",
    0x5CF543EB: "_LONGDOUBLE",
    0x5CF5A0ED: "SBRBITSTREAM",
    0x5CF8DF14: "GPUBLEND",
    0x5CF98663: "D3D::D3DFastVector",
    0x5CFBE111: "DC_SURFACE_0_EXTENT",
    0x5CFC2FAD: "PatInterface::CircleComment",
    0x5D0175B2: "cOmLadderAction_dummy",  # pc-only
    0x5D0882D2: "_XMSG_PROPERTY_ATTACHMENT",
    0x5D135717: "_XMUDEC4",
    0x5D15EBEB: "uOmCoopJumpBroad::cActPlJump",  # pc-only
    0x5D18AA00: "RB_SIDEBAND_DATA",
    0x5D1C1F14: "PA_SC_DEBUG_SR_0",
    0x5D1E35F7: "_DRC",
    0x5D1F8E76: "cEm34ActCoreWait",  # pc-only
    0x5D246454: "CCalBmpDecoder",
    0x5D291B29: "XECRYPT_SHA_STATE",
    0x5D291CAA: "NetworkRanking::BoardList",
    0x5D2E3BDE: "_XALLOC_ATTRIBUTES",
    0x5D2E6F95: "MtCylinder",
    0x5D3064D5: "_XMATCH_SESSION_DELETE",
    0x5D3AEDFF: "VocalFry_mblk",
    0x5D43D8E1: "MtCollada::Camera",
    0x5D43E5BD: "uOmCoopTreasure::cActOpening",  # pc-only
    0x5D4427FA: "_XMARKETPLACE_ASSET_PACKAGE",
    0x5D4AD9A8: "cEm8cActCoreRev",  # pc-only
    0x5D4C4B65: "std::_String_iterator",
    0x5D54625D: "PCIE_HDR_LOG3",
    0x5D54F147: "VGT_DRAW_INITIATOR",
    0x5D565CAD: "rEffect2D::KEYFRAME_STATUS",
    0x5D576BE9: "uOmSwitch::cActDisable",  # pc-only
    0x5D5883B5: "tagStreamIdnMediaType_WMC",
    0x5D652D84: "cEmc3ActOff",  # pc-only
    0x5D65D0AF: "uShadowLight::GROUP",
    0x5D73F3B5: "FSB_LX_IDLE_PATT_OR",
    0x5D7B1A82: "CP_RT1_COMMAND",
    0x5D7B8087: "FSB_LX_DADD",
    0x5D7CFA8C: "PIXPatchVertexShaderToMatchPixelShaderData",
    0x5D810605: "cAIPositionFilterObject",  # pc-only
    0x5D8514CF: "cEm40ActTouchTake",  # pc-only
    0x5D854116: "PIX_API_TYPE",
    0x5D872FA1: "XG_MCT::CXEncoder::CompressionType",
    0x5D8A857D: "FB_SIZE",
    0x5D8C1B95: "rEffectList::EFL_PARTICLE_HIT",
    0x5D8FE90D: "_RECORDTABLEVECTOR",
    0x5D901E26: "MtVector3",
    0x5D91D1C1: "NetworkRequest",
    0x5D9577E3: "MtFileStream::__vftable",
    0x5D97ABE5: "rEffect2D::LINE_TYPE",
    0x5D98239D: "CP_ME_RAM_RADDR",
    0x5D9CF389: "_DXVA_VideoChromaSubsampling",
    0x5D9DB323: "cEm10ActAtkStunRod",  # pc-only
    0x5D9EAC94: "BIU_PERFMON_CNTL",
    0x5DA0354C: "XONLINE_TEAM_LIVE_PERMISSIONS",
    0x5DA98297: "CRS_TIMER",
    0x5DAA041E: "NetworkError",
    0x5DB41E95: "_DXVA_COPPSetSignalingCmdData",
    0x5DB73816: "IOC_INT_VECTOR",
    0x5DC618BF: "uOmHourGlass::cActWait",  # pc-only
    0x5DC8973B: "DSPROPERTY_I3DL2_LISTENERPROPERTY",
    0x5DCBF52B: "cPlAction_pl_act_attack_knee_bazooka_fail",  # pc-only
    0x5DD3F3D2: "EP_MEM_BASE",
    0x5DD9430F: "_HVSTATS",
    0x5DDE513C: "XAUDIO::CXMemMemoryManager",
    0x5DE22E2C: "XUIMessageTimelineNotify",
    0x5DE888AF: "_D3DXMATERIAL",
    0x5DE99442: "PatInterface::SearchProperty",
    0x5DEDEEB6: "_XMICON4",
    0x5DF5EC93: "cTrans::IndexBuffer::MyDTI",
    0x5DF787FD: "HICON__",
    0x5DF8C93C: "uOmElevator::cActOpenReady",  # pc-only
    0x5DFB49E4: "_Q_LIST_REPLY_MSG",
    0x5E028057: "STREAMNAMESDESC",
    0x5E0335D8: "AZ1_AZ2BC_CRC_READ",
    0x5E04E488: "EFC_SEQ",
    0x5E07F360: "CQueueElement",
    0x5E08E93E: "cNetEm84",  # pc-only
    0x5E0923D7: "cScenario",  # pc-only
    0x5E0B19DA: "FSB_TX_PMC3",
    0x5E0F245F: "DO_TEST_DEBUG_DATA",
    0x5E11907D: "_FXLTECHNIQUEENTRY",
    0x5E1444ED: "cEm20ActAtkComboExtStart",  # pc-only
    0x5E1574B3: "MP4MovieHeaderAtom",
    0x5E18C560: "_DM_SWAPDISC_COMPLETE",
    0x5E1C9A87: "MC1_RD_STR_DLY_0",
    0x5E21A94A: "ID3DXFileSaveObject",
    0x5E21E574: "_XSHOWUPDATERUI_PARAMS",
    0x5E2219C9: "cEm44ActTakeOff",  # pc-only
    0x5E29FF8A: "XUI_SCROLLEND_STATE",
    0x5E2B5D1C: "CCalSubRenderer",
    0x5E374B51: "MC0_DLL_MASTER_ADJ_1",
    0x5E38204D: "PA_SU_PERFCOUNTER3_LOW",
    0x5E38C30C: "cEm70Action",  # pc-only
    0x5E3B2458: "SQ_PERFCOUNTER0_HI",
    0x5E3C51C2: "D1SCL_CRC_SOURCE_SEL",
    0x5E40AD97: "CAudioEncoderDynamicOverride",
    0x5E40C214: "MC0_RD_STR_DLY_CNTL",
    0x5E410CE7: "SCHEMA_CONFORMANCE_INFO",
    0x5E42C505: "cEmc0ActRepair",  # pc-only
    0x5E44957F: "MtCRC::__vftable",
    0x5E455A82: "MC0_INTERRUPT_MASK",
    0x5E466C0C: "uEffectVFR::PTCL_COLL_STATUS",
    0x5E478F09: "rEffectSetData::ResourceInfo::STATUS",
    0x5E49696C: "IMAGE_LOAD_CONFIG_DIRECTORY64",
    0x5E49D962: "tagWMVUserData",
    0x5E4C0CA4: "EFC_LOD",
    0x5E54F301: "PCIE_TX_CREDITS_CONSUMED",
    0x5E5557AF: "DM_XAM_SERVICES_1888",
    0x5E564915: "uChain::CollisionWork::MyDTI",
    0x5E5D124C: "MSI_MSG_CNTL",
    0x5E5E5556: "rObjAdj::Node",  # pc-only
    0x5E645B75: "TP_TC_CLKGATE_CNTL",
    0x5E646CDD: "cPlAction_pl_act_relax",  # pc-only
    0x5E6D9C11: "cEm40ActFarCatchOk",  # pc-only
    0x5E6E36E8: "_PASSPORT_SECRET_QUESTION",
    0x5E713A86: "D3D::StatusRegister",
    0x5E737D43: "cWind::MyDTI",
    0x5E7420C9: "XECRYPT_RSAPRV_1536",
    0x5E7B5E5E: "_TESTXEXXUILOCK",
    0x5E803D96: "CXLiveMessaging",
    0x5E8BE0A5: "SQ_PERFCOUNTER3_SELECT",
    0x5E8E3695: "RB_BLEND_BLUE",
    0x5E8EC6B9: "XDVO_CRC_MASK_SIG_RGB",
    0x5E8F4756: "MtCollada::Node",
    0x5E8FEADF: "uMovie::Player::Descriptor",
    0x5E9108FD: "DRM_AES_KEY",
    0x5E985D30: "cFSMOrderPawn::FuncParamSound",  # pc-only
    0x5E98F7AF: "XAUDIO::XAUDIOENGINECALLBACKCTX",
    0x5E99D842: "CCalDecoder::CreateParameters",
    0x5E9D190F: "CCalStream::STREAM_TYPE",
    0x5EA2B1CF: "_BCD80",
    0x5EA3DF1D: "cEm10ActPara_R",  # pc-only
    0x5EA5C4B9: "sCapture::FORMAT",
    0x5EA76CD7: "MH_PERFMON_PERFCOUNTER0_LOW",
    0x5EA95E61: "std::codecvt_base::__vftable",
    0x5EB44C4E: "_D3DXTRACK_DESC",
    0x5EBC58BB: "CCalImageDecoder",
    0x5EC52E08: "TCO_QUAD3_DEBUG1",
    0x5EC6D3CB: "uEffect2D::MoveAdd",
    0x5EC7180B: "uEffectEdit::PTCL_FLAG",
    0x5EC9F022: "_XMUHEND3",
    0x5ECB4D74: "PA_CL_POINT_CULL_RAD",
    0x5ECB80B4: "_IMAGE_OPTIONAL_HEADER",
    0x5ECDFD4E: "uEffectVFR::ClothVertex",
    0x5ED4A917: "cEm46ActBodyAttack_Pl",  # pc-only
    0x5ED4DC50: "sObjModel::CartridgeMgr",  # pc-only
    0x5ED5DE53: "MtFCurve::INTERPOLATION_TYPE",
    0x5ED72102: "cEm22ActTurn",  # pc-only
    0x5ED7335A: "cEm87ActWait",  # pc-only
    0x5EDAB4ED: "CFilter",
    0x5EDD7C3C: "MtPhysicalAllocator",
    0x5EE39460: "TCF_PERFCOUNTER9_LOW",
    0x5EE7D9EF: "cEm6dActFly",  # pc-only
    0x5EE8055E: "YCLK_CNTL1_REG",
    0x5EEF5113: "cNetEm63",  # pc-only
    0x5EF318BC: "_XPRESENCE_SYNC_SUBS_RESPONSE",
    0x5EF334AE: "XAUDIO::SRC::Native",
    0x5EF36A33: "_IMAGE_EXPORT_DIRECTORY",
    0x5EF3815B: "D1CRTC_V_TOTAL",
    0x5EF4752E: "sParameter::PLAYER_INFO_STRUCT",  # pc-only
    0x5EF49D7D: "_GET_USER_SUBSCRIPTION_DETAILS_DATA",
    0x5EF5E6AC: "cEm62ActWait",  # pc-only
    0x5EF66408: "CCalDecoder",
    0x5EF6D983: "BIUPERFEVENT",
    0x5EFAD990: "_GET_USER_INFO_REQUEST",
    0x5EFD31E8: "cNetEm70",  # pc-only
    0x5F00D190: "CCalImageMetadata::__vftable",
    0x5F019A62: "Decode1stSplStatus",
    0x5F01D565: "DSPROPERTY_I3DL2_BUFFERPROPERTY",
    0x5F04E491: "RB_PERFCNT_SELECT",
    0x5F05E7C8: "cOmCoopCardDoorEventPL",  # pc-only
    0x5F06566E: "BSAFE_PRV_KEY",
    0x5F0791CB: "_D3DXSHADER_TYPEINFO",
    0x5F08172D: "CXuiHtmlElement",
    0x5F08C17F: "IDirectXFileObject::__vftable",
    0x5F0929D8: "uOmS705ceil::cActKillEm",  # pc-only
    0x5F0D8E1C: "CG_SCRATCH1",
    0x5F0F12E9: "_XSTORAGE_DOWNLOAD_TO_DIRECTORY_PARAMS_INTERNAL",
    0x5F0F22E6: "RB_COLORCONTROL",
    0x5F11C085: "UCODESHADERMAGIC",
    0x5F1314BF: "cPlAction_pl_act_wall_stick_f_ready",  # pc-only
    0x5F135403: "cShape::WeightNode::ATTRIBUTE",
    0x5F1D005A: "MtGeomMinkowskiDiff::MyDTI",
    0x5F204258: "cEm34ActDie",  # pc-only
    0x5F237608: "PARSERSTATE",
    0x5F2D10DF: "_XCONFIG_MEDIA_CENTER_ENTRIES",
    0x5F3089C1: "sPrim::MyDTI",
    0x5F323500: "GPUCULL",
    0x5F34B687: "cOmDeadAction_dummy",  # pc-only
    0x5F35ECA6: "sSoundN::MultiBandEQUnit",
    0x5F36690F: "cEm80ActSyutoRevGo_PL",  # pc-only
    0x5F36B659: "rAIWayPoint",  # pc-only
    0x5F3A8EBB: "rNavigationMesh::nodeInfo",  # pc-only
    0x5F3CAB7B: "FSB_TX_PMC1_AND",
    0x5F3E42AC: "rEffectList::FILTER_TYPE",
    0x5F3F109D: "_DM_SATA_CHANNEL_DATA",
    0x5F424764: "XAUDIOFXMGRINIT",
    0x5F43FA97: "XUINotifyComboBoxListOpening",
    0x5F4700DE: "stat",
    0x5F4B6C18: "PA_SU_POLY_OFFSET_BACK_SCALE",
    0x5F4CA1C9: "XUIFigurePoint",
    0x5F51A7DD: "rSoundRequestXml::MyDTI",
    0x5F58B068: "PatConnection::RW_HEAD",
    0x5F5A7661: "RB_COPY_MASK",
    0x5F62438E: "_s__RTTIBaseClassDescriptor2",
    0x5F665A63: "cOmCoopGateAction_sub",  # pc-only
    0x5F68C17A: "uGridEnvLight::MyDTI",
    0x5F69AF3E: "_Q_DELETE_MESSAGE_MSG",
    0x5F6BEB05: "cOmCoopBoxAction_om_act_now_break",  # pc-only
    0x5F72395E: "_DXVA_VideoPropertyRange",
    0x5F72BC7B: "CRTC1_DEBUG_02",
    0x5F7429C9: "cEm0bActAtkCatch",  # pc-only
    0x5F758BE2: "cPlAction_pl_act_ready_wait_side",  # pc-only
    0x5F7624D6: "MP4EditAtom",
    0x5F76C9C3: "_D3DMATERIAL9",
    0x5F7C55D4: "AZ1_MRU_BANK5_DEPTH_MASK",
    0x5F7FD401: "_ACCOUNT_QUERY_REQUEST",
    0x5F810788: "cAIPathTrace::TracePoint",  # pc-only
    0x5F813CB8: "MtAllocator",
    0x5F84977A: "cEm10ActDmgYoroke",  # pc-only
    0x5F84F7C4: "rMovieOnMemory",
    0x5F853E28: "D1CRTC_CONTROL",
    0x5F8998BE: "VGT_EVENT_TYPE",
    0x5F8C73C0: "CP_DMA_DST_ADDR",
    0x5F8E436E: "cEm6dActDieIce",  # pc-only
    0x5F8FD635: "cEm10ActAtkPlagaHeadDash",  # pc-only
    0x5F907391: "_D3DXPARAMETER_CLASS",
    0x5F91497C: "sKeyboard::VKMAP",
    0x5F917139: "rSoundDirectionalCurveXml::Curve::MyDTI",
    0x5F95DFD0: "ENC_MEM_BLK",
    0x5F973EEE: "_XNQOSHISTORYENTRY",
    0x5F9890E3: "uOceanWater::WATER_VERTEX",
    0x5F9C3439: "CCalImagePlayer",
    0x5FA0A1CB: "PIX_INDEX_AUDIO",
    0x5FA144CF: "CP_RT13_REFERENCE",
    0x5FA167E3: "PCIE_PERF_LATENCY_TIMER_HI",
    0x5FA1A093: "DelayedCopyField_Ctl",
    0x5FA1F311: "_AUDIO_OBJECT_TYPE",
    0x5FA7DC8C: "CP_RT3_MASK",
    0x5FA7F6ED: "cAIOctTree",  # pc-only
    0x5FA816DE: "cEm20ActDieIce",  # pc-only
    0x5FAB98CB: "RB_PERFCOUNTER2_HI",
    0x5FB3D22E: "tagMotionVector_WMV",
    0x5FB57A9C: "NetworkSessionStable::Adjust",
    0x5FBA3B99: "_D3DVBLANKDATA",
    0x5FC3CC47: "PSRO_REG",
    0x5FC47549: "uOmClutch::cActBurnt",  # pc-only
    0x5FCD5715: "cEm20ActAtkComboExtEnd",  # pc-only
    0x5FD2D281: "cMaterial::TYPE",
    0x5FD60C19: "CP_RT11_POLL_ADDRESS",
    0x5FDF78DF: "D3DSurface",
    0x5FDFEE7A: "TCF_PERFCOUNTER3_HI",
    0x5FE28647: "uOmJeep::cActWepDeadFall",  # pc-only
    0x5FE447B8: "_tag_AMVABeginFrameInfo",
    0x5FE55033: "GPUCmdRangeRed",
    0x5FE824E0: "BIU_FSB_XMIT_ARB_CNTL",
    0x5FEE0946: "sMain::JOB_WORK",
    0x5FEE5C61: "_QUERY_ADD_RESULT",
    0x5FEF2A00: "cEm8cAtkDrillDie",  # pc-only
    0x5FEFCE79: "tagFrameCodingModeInfo",
    0x5FF52FC4: "_STRING_LOOKUP_RESPONSE",
    0x5FFF1C3F: "ISORGBColor",
    0x60002AB6: "uOmS705ceil::cActBreak",  # pc-only
    0x6002E43A: "CCalWmaEncoder",
    0x60075B45: "sMouse::STATE",
    0x600D078F: "CCalBase::STOP_FLAGS",
    0x60134A78: "_FP_64",
    0x60141CC0: "CCalMediaMetadata::__vftable",
    0x601BF5FE: "_FP80",
    0x601FEC97: "_EX_XCONFIG_REGISTRATION",
    0x602488C3: "FSB_TLA_PATTERN_CONTROL",
    0x602C2C91: "_D3DTESSELLATIONMODE",
    0x602C79C8: "cFSMOrderPawn::FuncParamPosition",  # pc-only
    0x60384A25: "CACHE_NON_MAIN_MEM_BAR",
    0x603AC047: "cTrans::ZPASS_MODE",
    0x603B9C6D: "uOm1317_S109_Glass::cActCrack",  # pc-only
    0x603DEEEE: "cEm84PlEvent_Ashibarai",  # pc-only
    0x603EACAB: "_XWMDRM_CERTIFICATE_PUBLIC_KEY",
    0x604A95B7: "NEWINDEXSPECIFIER",
    0x604D8B53: "_XSTORAGE_FACILITY_INFO_GAME_CLIP",
    0x604F1D10: "_RTL_CRITICAL_SECTION",
    0x604FCF85: "CAacDecoderDynamicData",
    0x60524FBB: "rShapeWeight",
    0x605804AB: "DOUT_DEBUG",
    0x60587D07: "AZ1_LOOPBACK_AZID",
    0x60588D52: "cEm41AActNormal",  # pc-only
    0x605B7510: "cEventAct",  # pc-only
    0x605F4CA6: "XMSG_INVITE_ANSWER_TYPE",
    0x605F9263: "_D3DFILTER_TYPE",
    0x6060DD77: "uOm1303_Truck::cActAttack",  # pc-only
    0x6064D335: "rEffectList::GENERATOR_TYPE",
    0x60654804: "_OBJECT_SYMBOLIC_LINK",
    0x6068EDFF: "MtCalculator::ERR",
    0x606D6246: "cEm0bActAppear",  # pc-only
    0x60711D85: "rSoundSourceSEInterMediate::MyDTI",
    0x6072B3C8: "CNativeEndianBuffer",
    0x607605C1: "VGT_GROUP_VECT_1_FMT_CNTL",
    0x608113CD: "TCB_FETCH_GEN_SECTOR_WALKER1_DEBUG",
    0x60842DCC: "rClothXml::Constraint",
    0x6086A6C5: "D1GRPH_LUT_AFTER_CSC",
    0x60894634: "XONLINE_PASSCODE_TYPE",
    0x608948B0: "cAIQuadTree",  # pc-only
    0x608AFE32: "_XAMGETPERSISTMEMFUNCS",
    0x608BA1D4: "_RTL_HEAP_USAGE",
    0x608FFDB6: "RTV_CODEC",
    0x6093B93C: "uOm0934::cActBurnt",  # pc-only
    0x6094A677: "PCIE_CRS_COUNT",
    0x609C653B: "uOmHourGlass::cActBase",  # pc-only
    0x609FF193: "uEffectEdit::ModelKeyframe",
    0x60A41D8F: "cEm42ActEnter",  # pc-only
    0x60A5647C: "DM_STREAMSTATUS",
    0x60A6DC3B: "CXuiModule",
    0x60A80C09: "_IMAGE_DATA_DIRECTORY",
    0x60ADAF2D: "_D3DXCOMPRESSION_FLAGS",
    0x60AF2A2B: "cOm0200ActDown",  # pc-only
    0x60B02C8B: "XONLINE_PAYMENT_TYPE",
    0x60B0A509: "PCIE_RX_CREDITS_ALLOCATED",
    0x60B1426F: "rEffectList::EFL_PARTICLE_COMMON",
    0x60B1D6C6: "XConfigSecuredSettings",
    0x60B452F0: "cNetEm42Core",  # pc-only
    0x60B4BEE6: "CMp3Decode",
    0x60B5BE5C: "_s__RTTICompleteObjectLocator",
    0x60B7328B: "cEm0bAction",  # pc-only
    0x60B77E0B: "IOC_CPU_SLV_REQ_ARB",
    0x60B89222: "CP_RT0_BADR",
    0x60BC7CDA: "RB_BLENDCONTROL2",
    0x60BE01FD: "PIX_XAUDIO_COUNTERS",
    0x60C10879: "uHemiSphereLight",
    0x60C7F946: "MC1_CRC_READ",
    0x60C804EB: "cEm42ActDead",  # pc-only
    0x60C81C66: "cPlAction_pl_act_item_load_second",  # pc-only
    0x60DD2842: "cSetInfoOmBackupHeli::Area",  # pc-only
    0x60EF7E42: "_XMUSHORTN2",
    0x60F411B1: "PIX_XAUDIO2_COUNTERS",
    0x60F5D817: "CP_PFP_UCODE_DATA",
    0x60F6EC0A: "sParameter::RANGE_PARAM",  # pc-only
    0x60FB2DE5: "uOmElevator::cActPlReady",  # pc-only
    0x60FCA92F: "_PASSPORT_GET_MEMBER_NAME_RESPONSE",
    0x60FD04E6: "_RC4_SHA_HEADER",
    0x60FD97C4: "cEm43ActDownStart",  # pc-only
    0x6105EFCC: "D1SCL_VERT_FILTER_CONTROL",
    0x6105F406: "_FILE_ACCESS_INFORMATION",
    0x6106E4BF: "PredefinedXformType",
    0x61094D8D: "PIXMetaResolveDestTextureData",
    0x610F7090: "D3DVertexShader",
    0x610F9727: "D1OVL_ALPHA_INSIDE_OVL_WINDOW",
    0x611391BC: "_PASSPORT_GET_BUDDY_GAMERTAG_RESPONSE",
    0x6118275C: "XAUDIO::CIrql",
    0x6119F98B: "_D3DFOGMODE",
    0x611A2B40: "MULTIRES_PARAMS",
    0x611C94D9: "SLOT_CNTL",
    0x61272051: "XGI_WRITEGAMERTILE2_MSG",
    0x6128890A: "RTS_INV_W_DX",
    0x612976E8: "cPlAction_pl_act_run",  # pc-only
    0x612DF6E2: "sCapture",
    0x6136CD94: "_P_ALIVE_2_MSG_INTERNAL",
    0x613B2AB2: "rEffectSetDataList",
    0x613ED169: "XAUDIO::CBatchAllocator",
    0x6140037E: "_XUPDATE_DOWNLOAD_RESULTS",
    0x6140D386: "CCalWavEncoder::IffHeader",
    0x61423731: "XAUDIO::_XMA_CONTEXT_DATA",
    0x6143BD7B: "uEffectVFR::Particle",
    0x6144098D: "_XAMPOWERMODE",
    0x61450CD2: "GpuResiduals",
    0x61499E6E: "uEffectEdit::Filter",
    0x614EF08D: "uOmAreaCoop::cActCoop",  # pc-only
    0x6151EED4: "cLinkUnitDispAttr",  # pc-only
    0x615384D8: "CCalDecoder::__vftable",
    0x6155F48C: "_CREATE_LIVE_ACCOUNT_REQUEST",
    0x615FDE72: "cEm43Action",  # pc-only
    0x61623238: "_XCONTENT_REFRESH_LICENSE_REQUEST",
    0x6166A724: "RB_HSIO_DLL_ADJ9",
    0x6167A960: "sCapture::ANTIALIASING",
    0x616A245F: "FSB_TX_PMCTRL_AND",
    0x616A79F7: "_D3DTRILINEARTHRESHOLD",
    0x616F7A89: "rSoundRandom::Element",
    0x616F98A9: "cWpAction_wp_act_bomb",  # pc-only
    0x6170ECA4: "_XCONFIG_STATIC_SETTINGS",
    0x61727478: "CXStorageMiscParent",
    0x617375CF: "tagWMVSyncAV",
    0x617590B8: "HEADER",
    0x61778A08: "MtFloat2A",
    0x617B78A1: "std::basic_ios",
    0x617E62FC: "D3D::RegisterDescription",
    0x617E6FA3: "GPUSURFACENUMBER",
    0x617FB797: "MtCollada::Channel::MyDTI",
    0x61814B7E: "rEffectSetData::KF_ID",
    0x61853BA2: "_XUSER_DATA",
    0x618F3C52: "cEm83ActPinioned",  # pc-only
    0x618FBD73: "_XMDHEN3",
    0x6190B55B: "MtXmlWriter::__vftable",
    0x6192126B: "BIOS_2_SCRATCH",
    0x6192DD37: "ISequentialStream",
    0x6194D095: "XONLINE_VIDEO_QUALITY",
    0x6195AF10: "rLayout::SetInfo",  # pc-only
    0x6195D6BA: "CLIPPER_DEBUG_REG09",
    0x61965FD8: "FSB_LX_LERST_XSTP_OR",
    0x619B28BB: "CP_RT4_REFERENCE",
    0x619CB19E: "_FXLRENDERSTATEDATA",
    0x619F5E9E: "uMultiRadialBlurFilter::MyDTI",
    0x619FBED1: "_DXVA_ConfigPictureDecode",
    0x61A22511: "XONLINE_GET_POINTS_BALANCE_DETAILS_RESPONSE_FLAGS",
    0x61A28943: "ScrHideArea",  # pc-only
    0x61A60A63: "PA_SC_DEBUG_ITER_0",
    0x61A95ED5: "_TOKEN_INFORMATION_CLASS",
    0x61AD93C8: "ANON_OBJECT_HEADER",
    0x61BADD04: "rEffectList::BILLBOARD_TYPE",
    0x61BE1FDD: "PCLK_SOFT_RESET",
    0x61CC1272: "FileMappingObjectRecord",
    0x61D0130E: "CP_MEQ_AVAIL",
    0x61D0A992: "XAUDIODRVRENDERFXCALLBACK",
    0x61D0E79F: "_GET_POINTS_BALANCE_RESPONSE",
    0x61D32A01: "TCF_PERFCOUNTER7_LOW",
    0x61D75397: "rCameraXml::__vftable",
    0x61DAA45A: "_IMAGE_ROM_HEADERS",
    0x61DC0875: "cAnimColor",  # pc-only
    0x61DD0699: "rEffect2D::KEYFRAME_INP_TYPE",
    0x61DE35FC: "VGT_GROUP_FIRST_DECR",
    0x61E240BA: "cOmTestAction_om_act_wait",  # pc-only
    0x61E50998: "rSoundStreamRequestXml",
    0x61E71058: "_XUSER_PLAYERLIST_USER_INTERNAL",
    0x61E733F4: "PCIE_CAP",
    0x61E791BA: "_VD_DRIVER_OPTIONS",
    0x61E85DB5: "FSB_TX_CMDMM1_OR",
    0x61E91BBF: "HMENU__",
    0x61E9CCEC: "DC_LUT_AUTOFILL",
    0x61EA55B9: "sPad::PAD_REPEAT",
    0x61EF8C99: "XMEDIA_VIDEO_FORMAT",
    0x61F2F00D: "_D3DXSHPRTCOMPBUFFER_DESC",
    0x61F49C07: "NetworkPeer::__vftable",
    0x61F5F8F9: "_ULARGE_INTEGER",
    0x61F8EBC3: "D3DTexture",
    0x61FC6496: "_OSVERSIONINFOEXA",
    0x61FD2CE8: "CXuiNavButton",
    0x6203B987: "TCB_TAG2_DEBUG",
    0x6204F51F: "CP_RT4_POLL_ADDRESS",
    0x62050155: "ID3DXIncludeVtbl",
    0x6205DDF9: "GUID",
    0x620702DA: "_XMCOLOR",
    0x6207C685: "MP4HandlerAtom",
    0x620885EF: "_OFFER_PRICE",
    0x620AA181: "cEm32DmgAction",  # pc-only
    0x620BCFD4: "sParameter::ITEM_INFO_STRUCT",  # pc-only
    0x620E5538: "_P_PEER_SUBSCRIBE_REPLY_MSG",
    0x6212458D: "XAUDIO::CEffectManager::__vftable",
    0x6212BFC3: "EP_ADAPTER_ID",
    0x6214D8E4: "CP_STQ_RT_ST_STAT",
    0x6218B851: "PCIE_FC_P",
    0x621A590B: "_ACCOUNT_CHANGE_GAMERTAG_REQUEST",
    0x621B542B: "_STFC_HASH_BLOCK",
    0x62201F82: "cEm63ActWalk",  # pc-only
    0x622090D2: "XAUDIO::CEffect::__vftable",
    0x622BB32D: "cEm10ActDownRoll_L",  # pc-only
    0x62331FBF: "_XPROFILE_ENUM_ACHIEVEMENTS_RESULT",
    0x62351EFD: "_LIST_ENTRY",
    0x6236D328: "XNOTIFICATION_DEQUEUE_STATE",
    0x62425C3F: "XSVENGINE",
    0x62428CA2: "INPUTSRCGETDATAINSTANCE",
    0x62439845: "uOm0026::cActStart",  # pc-only
    0x62519716: "_P_INVITE_ANSWER_MSG_INTERNAL",
    0x6253A16F: "LB_DISP1_SPLIT_REQ",
    0x6255976C: "_DXVA_DeinterlaceBltEx",
    0x625A63B0: "sLightLinker::uCapsule",  # pc-only
    0x625C82CB: "FSB_TX_PMC0_AND",
    0x625F594B: "_Q_MESSAGE_SUMMARY",
    0x6261FE46: "_FXLTECHNIQUE_DESC",
    0x626481A2: "uOmSwitch::cActSwitchWait",  # pc-only
    0x6267B04D: "XAUDIOVOICEOUTPUTVOLUMEENTRY",
    0x626B6700: "_IMAGE_XEX_HEADER",
    0x626D6BC3: "_D3DXREGISTER_SET",
    0x626EAD80: "uTVNoiseFilter::MyDTI",
    0x6270EC61: "sPhysics::CONSTRAINT_TYPE",
    0x627AEC6F: "cEmc6ActWait",  # pc-only
    0x627B653E: "CXuiEdit",
    0x627D858A: "_s_ESTypeList",
    0x627DEB22: "MP4PaddingBitsAtom",
    0x627FA9F0: "cEm32ActAtkJump",  # pc-only
    0x628138D4: "EFC_KF_INP_TYPE",
    0x6285E5D3: "uOm08e9_S303Elev::cActFall",  # pc-only
    0x62873F47: "GpuCommon",
    0x628C0CC1: "TCD_INPUT3_DEBUG",
    0x6290C070: "PA_CL_VPORT_ZSCALE",
    0x6291F28A: "uHavokJob",  # pc-only
    0x629372ED: "NetworkSingleTcp",
    0x629446F1: "PA_SU_POINT_MINMAX",
    0x6298603B: "DC_SURFACE_2_BASE",
    0x6298E6AD: "EFC_MATRIX_TYPE",
    0x629D7207: "uColorSpaceFilter",
    0x629EC706: "_XEIKA_CERT_OVERLAY",
    0x62A04B00: "XUIMessageTransition",
    0x62A0F1AD: "FSB_TLA_STATUS_CONTROL",
    0x62A25A96: "CContentAndUpdateBase",
    0x62A8D89E: "_XFILECACHE",
    0x62AD0EFC: "_MESSAGE_RESOURCE_DATA",
    0x62ADAC8C: "_STF_CONTROL_CODE",
    0x62B9AA87: "_GET_PAYMENT_INSTRUMENTS_RESPONSE",
    0x62C31EE2: "RB_COPY_FUNC",
    0x62C35B9D: "D3DXVECTOR4",
    0x62C806CA: "rScheduler::KEY::MODE",
    0x62D0D48C: "sParameter::WEAPON_MOUSE_AIM_STRUCT",  # pc-only
    0x62D2ABF0: "_XAM_BOOT_REASON",
    0x62D5DF00: "_XNET_LOGON_SERVICE_INFO",
    0x62D6C4E1: "cOmHavokAction_wait",  # pc-only
    0x62D89304: "_STRING_WITH_HRESULT",
    0x62DF287A: "_XONLINE_STATS_SPEC",
    0x62E144B3: "cPlAction_pl_act_coop_item_load_first",  # pc-only
    0x62E1527F: "XDVO_BIT_DEPTH_CONTROL",
    0x62E435FB: "_DXVA_Qmatrix_H264",
    0x62E52C90: "sSoundN::Voice",
    0x62EDCB09: "NetworkLayer::Position",
    0x62EF6D9B: "cEm41ActDisclose",  # pc-only
    0x62F054E2: "_XUSER_PLAYERLIST_USER",
    0x62F0CD1A: "AZ1_ZPASS_SAMPLES",
    0x62F28B85: "sMouse::MyDTI",
    0x62F3F60C: "XECRYPT_RSAPRV_2048",
    0x62F549C7: "AZ1_SECONDARY_STATE_DWORD2",
    0x62F8A9B6: "_P_INVITE_ACTION_ITEM",
    0x62FAB160: "_RECORDTABLE",
    0x62FB0FF8: "cTrans::ArrayTexture",
    0x62FB3C73: "FSB_TLA_FREEZE_CONTROL",
    0x62FD20CF: "_PM4CMDDRAWINDXIMMEDIATE",
    0x62FDE667: "LB_SCL1_READ",
    0x62FE9EEB: "XRL_TRANSACTION_STATE",
    0x63081E49: "_P_ACCEPT_REQUEST_MSG",
    0x630CB795: "GC_SUB_CLASS",
    0x630E5440: "IClassFactoryVtbl",
    0x630E9A41: "NetworkUniqueId::Core",
    0x630F6A0E: "PA_SC_PERFCOUNTER2_HI",
    0x6313C8ED: "MtPreProcessor::LINE_INFO",
    0x6313DE28: "CXuiScrollBar",
    0x6318A736: "CP_CONST_ID",
    0x6318E0E8: "GPUSYNCSPACE",
    0x63196421: "HPALETTE__",
    0x6319FC1F: "PCIE_PERF_COUNT0_SLV_R_CLK",
    0x631BB6EB: "DOUT_DEBUG_ID",
    0x631CE817: "waveformat_tag",
    0x6322AA34: "D1SCL_HORZ_FILTER_SCALE_RATIO",
    0x6322B585: "MtCollada::Matrix::MyDTI",
    0x6325AC00: "CXuiCheckbox",
    0x632E1CC7: "XGI_CLEARTITLE_MSG",
    0x63334077: "WMVFrameType",
    0x633926EE: "cEm10ActBackHoldEscape_PL",  # pc-only
    0x633C18BE: "PCIE_TX_REQUESTER_ID",
    0x633E555E: "stdext::exception::__vftable",
    0x63420513: "HBRUSH__",
    0x6343BB79: "sMain::JOB_WORK32",
    0x634A8E25: "CP_RT12_SIZE",
    0x634CDF08: "tagWMVEntryPoint",
    0x63549129: "_XMATCH_DEAD_SG",
    0x635793CA: "rChain::Header",
    0x635809FD: "PA_SU_PERFCOUNTER2_LOW",
    0x63596E46: "FSB_LX_PMC5",
    0x6359F1FB: "tagVideoProfile_WMC",
    0x63611886: "cAIPositionPickUp",  # pc-only
    0x6366D195: "_LAST_EXCEPTION_LOG",
    0x6367BB01: "XAUDIO::XMA_PLAYBACK_CREATE",
    0x63681D8B: "sRender::INTERVAL_TYPE",
    0x636B99D9: "NetworkSessionManagerLive::LivePropertyMap",
    0x636C56E4: "D3D::BeginVerticesData",
    0x637021A1: "DLSLOOP",
    0x6375D979: "cEmA2ActHumituke_PL",  # pc-only
    0x63761ADE: "GPUMIPFILTER",
    0x6376F62D: "GC_BIST",
    0x63790BA0: "type_info",
    0x637C2423: "sPad::PAD_INFO",
    0x637D36AF: "_XPROFILE_CONTROL_SENSITIVITY_OPTIONS",
    0x637E9E5D: "SQ_FETCH_RT_0",
    0x637F68F4: "uOmClutch::cActClutch",  # pc-only
    0x637FC5E8: "_D3DXSHADER_DEBUGINFO",
    0x63829190: "cEm44ActLand",  # pc-only
    0x6383BDD0: "TCF_PERFCOUNTER8_LOW",
    0x638601EB: "_P_TEAM_REMOVE_MSG",
    0x63887B26: "PGL_CTL1",
    0x638C0B19: "TP2_PERFCOUNTER1_SELECT",
    0x638F682F: "cEm60ActDie",  # pc-only
    0x6394ED70: "cPlAction_pl_act_attack_knee_bazooka_first",  # pc-only
    0x639F3E3B: "_QUERY_SEARCH_RESULT",
    0x63A30100: "_XARB_TIMEEXTEND_REQUEST",
    0x63A7CA4C: "rSoundDirectionalSetXml::MyDTI",
    0x63A89930: "MtCollada::Joints",
    0x63AE3637: "VGT_PERFCOUNTER3_HI",
    0x63B1C445: "AZ0_LOOPBACK_PATTERN_CONTROL",
    0x63B44EDF: "MPLL_CNTL_REG",
    0x63B4F328: "GPUSURFACESWAP",
    0x63B70C12: "sKeyboard::KB_TYPE",
    0x63B7490B: "cEm3401ActWait",  # pc-only
    0x63BC7360: "CBitrateMonitor",
    0x63BE7C3D: "PatInterface::Ticket",
    0x63C177DD: "IXAudioRefCount::__vftable",
    0x63C74567: "MH_PERFMON_PERFCOUNTER1_LOW",
    0x63C78CB6: "BIOS_9_SCRATCH",
    0x63C8AADA: "ID3DXBaseEffectVtbl",
    0x63CF2EEC: "MC1_PERFCOUNTER0_LOW",
    0x63D02CE0: "AZ0_SECONDARY_STATE_DWORD2",
    0x63D6281B: "uProjectionEffect::MyDTI",
    0x63DDA384: "CP_NV_FLAGS_0",
    0x63DEA761: "cNetEm0c",  # pc-only
    0x63E0B536: "rEffectList::EFL_PARTICLE_FILTER_COMMON",
    0x63E298A0: "MtCollada::Pass::MyDTI",
    0x63E4636D: "cPositionEvaluationVisibilityThroughToPos",  # pc-only
    0x63E5581F: "REG_MACRO_ADDR_5",
    0x63E58ECD: "uOmCrank::cActPlLeave",  # pc-only
    0x63E648E5: "XONLINE_DMP_STATUS_TYPE",
    0x63E694FB: "tagDecode_mblk",
    0x63EA4AD4: "MtCollisionTree::Node::MyDTI",
    0x63EE14CA: "cAnimBase::KeyBase",  # pc-only
    0x63FA4FC9: "_SCALER_PARAMETERS_NOTIFICATION",
    0x6404B2DE: "PA_CL_VPORT_YSCALE",
    0x640601E4: "princeton_digital::stereo_room_t",
    0x64087B34: "sPrim::Prim",
    0x640A1295: "cPlAction_pl_act_attack_knife_plaga",  # pc-only
    0x64135A44: "SQ_FETCH_RT_4",
    0x64153E2D: "IXAudioRefCountVtbl",
    0x6419A8CB: "uModelEdge::BLENDOP",
    0x641AE85B: "cEm80ActAtkLowKickHit_PL",  # pc-only
    0x641D5A53: "cEm32ActWalk",  # pc-only
    0x641D6F9B: "XUICacheSceneAsync",
    0x641DBAC4: "MtHeapAllocator::HEAP_INFO",
    0x6425B0C4: "_D3DXATTRIBUTEWEIGHTS",
    0x642756FD: "MP4SampleToChunkAtom",
    0x6428A9EB: "XUINotifyFocus",
    0x642A8C07: "cScrHiding",  # pc-only
    0x642AADCC: "FSB_LX_PMCTRL_OR",
    0x642BC25F: "std::overflow_error",
    0x642D960F: "_IO_PRIORITY",
    0x6434AA5F: "FSB_LX_PMC1",
    0x6436C32C: "CARDEA_CSP_INTERFACE::__vftable",
    0x643AA1FA: "princeton_digital::allpass_t",
    0x6445BA5D: "cEm8ePlEvent_Tornado",  # pc-only
    0x644713EF: "_BANNER_HOTLIST_ENTRY",
    0x644E389B: "uEffectGenerator::MyDTI",
    0x64514E18: "NetworkLayer::Child",
    0x6452DE6E: "DO_TEST_DEBUG_OUT_CNTL",
    0x64536A6D: "RB_AZ_BC_CRC_MASK",
    0x645435CF: "princeton_digital::twotap_t",
    0x645D3A13: "cEm32ActDmgS",  # pc-only
    0x645D53C6: "uModelPlaneClip::MyDTI",
    0x6463F783: "_XMSG_GAME_INVITE_CANCEL",
    0x6469A506: "uOmKickSwitch::cActWaitKick",  # pc-only
    0x646C05AF: "_D3DXTARGET_DESC",
    0x646DB382: "_GRADUATE_USER_REQUEST",
    0x64766F50: "uOm0892_Lift::cActPlWait",  # pc-only
    0x647DA30E: "CP_STQ_ST_STAT",
    0x647FB6CF: "uFeedbackBlurFilter::MyDTI",
    0x6481A94B: "_ACCOUNT_RESERVE_GAMERTAG_REQUEST",
    0x6482DE67: "tagMediaType_WMC",
    0x64859461: "XnTitleState",
    0x64889C06: "REG_MACRO_ADDR_1",
    0x648D7E36: "cEm84CoreActStrippedAtk",  # pc-only
    0x6492A3E2: "cEm70ActJumpAttack",  # pc-only
    0x6497FF04: "PCIE_PERF_CNTL_SLV_S_C_CLK",
    0x649E9853: "GUID_WM",
    0x64A11373: "_s__CatchableType",
    0x64A34520: "rSoundSource",
    0x64A82E91: "GPUCOLORFORMAT",
    0x64A84806: "MtFile::FileInfo::MyDTI",
    0x64AC9975: "NetworkLayer",
    0x64AD0AF2: "BIU_INT_SNOOP_TIMEOUT_ADDR",
    0x64B59814: "RB_HSIO_PHASE_CAPTURE",
    0x64B7B09A: "IDirectXFileData",
    0x64B7CAD4: "cEm22ActGetup",  # pc-only
    0x64B8BA30: "SECURE_BUFFER",
    0x64BE6436: "rShape::MyDTI",
    0x64C00555: "uFlickerLight",  # pc-only
    0x64C6F221: "_XCONTENT_CROSS_TITLE_DATA",
    0x64C9D06B: "tagFrameTypeinfo",
    0x64C9EF7D: "CCalMediaInfo",
    0x64CE8F0E: "cPlAction_pl_act_damage_wesker_blow_wall_hit",  # pc-only
    0x64D2718E: "_FILE_INFORMATION_CLASS",
    0x64DA27D5: "DO_TEST_DEBUG_BUS_CLK1_SEL",
    0x64DA7463: "cEm10ActIgniteWeapon",  # pc-only
    0x64DE82BF: "_KPROCESS",
    0x64E22A33: "uOmExplosive::cActWait",  # pc-only
    0x64E70210: "_GET_LINKED_GAMERTAG_REQUEST",
    0x64EA1111: "uScreenMap",
    0x64ED0846: "uOmSwitch::cActBase",  # pc-only
    0x64ED79BA: "uOm1317_Glass::cActCrash",  # pc-only
    0x64EED369: "uEffectEdit::MovePathStrip",
    0x64F62647: "CP_RT2_COMMAND",
    0x64FBDD56: "ROOT_STATUS",
    0x64FC3CA4: "_XCOMPRESS_FILE_HEADER_LZXNATIVE",
    0x64FCF8B6: "XAUDIOFRAMEBUFDATA",
    0x64FDB389: "SUB_BUS_NUMBER_LATENCY",
    0x65049535: "uCrossFadeFilter::MyDTI",
    0x650C3907: "cEm0cPlEvent_Caught",  # pc-only
    0x650D263E: "cEm22ActDmgStaggers",  # pc-only
    0x650E155D: "_WMAPlayerInfo",
    0x6518B119: "ID3DXFileData",
    0x6524B3B8: "XUIMessageSetTeletypeCount",
    0x65284DE5: "uAftPlayer",  # pc-only
    0x652911AD: "rEffectList::EFL_PARAM_LINE_ZIGZAG",
    0x65295229: "cResource::QUALITY",
    0x652AD266: "XAUDIOCHANNELVOLUME",
    0x652F54B5: "_XSTORAGE_DOWNLOAD_TO_MEMORY_PARAMS",
    0x65379510: "tagStreamIdPattern_WMC",
    0x653D4770: "cAIFSM::Condition",  # pc-only
    0x653FE260: "rModelMontage::PARTS",
    0x654154ED: "CP_RT_ME_RAM_DATA",
    0x65418401: "AZ1_MRU_BANK12_DEPTH_MASK",
    0x6543BA02: "rEffectList::EFL_MOVE_PATH_COMMON",
    0x6547EE19: "PCIE_UNCORR_ERR_MASK",
    0x654F9E54: "D3D::CXpsGlobal",
    0x65589510: "cEm32ActAtkMountCeilToGround",  # pc-only
    0x655E32F2: "rSoundDirectionalSet::List",
    0x655E67E5: "CP_RB_RPTR_WR",
    0x65626FAA: "cEm80ActNoMove_PL",  # pc-only
    0x6562AA68: "NetworkRankingLive::moveInitNetwork::__l3",
    0x6564AD2E: "tPACKET_PARSE_INFO_EX",
    0x65681E00: "TCO_QUAD2_DEBUG0",
    0x65716E55: "SB_VENDOR_ID",
    0x6579DB23: "XAUDIO::XMA_PLAYBACK_ERROR",
    0x6579EFD1: "cEm10ActDmgHead",  # pc-only
    0x657CC523: "uOma00b_LaserArea::cActLaser",  # pc-only
    0x657D372C: "XDVO_DATA_STRENGTH_CONTROL",
    0x657E6EC0: "FSB_TX_DEBUG_LO_AND",
    0x658362F0: "XONLINE_PARENTAL_CONTROL_GROUP_TYPE",
    0x65839131: "XAUDIOSOURCEFORMAT",
    0x6583F0B4: "_XCONTENT_DOWNLOADMEDIA_GET_INPROGRESS_METADATA",
    0x6585D39E: "cEm43ActHeadAttack",  # pc-only
    0x6588661C: "MtMemoryStream::MODE",
    0x65889366: "sSoundN::MultiBandEQBaseUnit::FilterType",
    0x658AFDF2: "XAUDIO::XAUDIOSRCVOLUME",
    0x658B58AD: "FSB_LR_DEBUG_AUX",
    0x658CDD50: "uSchedulerEdit::MyDTI",
    0x6590AD3C: "rModel::MATERIAL_INFO::VTYPE",
    0x6592DF49: "PAYLOADEXTSYS",
    0x659722BA: "AZ0_MRU_BANK13_DEPTH_MASK",
    0x659C7ED0: "uOmAreaCoop::cActWait",  # pc-only
    0x65AD019D: "XUINotifyPressing",
    0x65AD09B1: "RTS_WD_EDGE_1_DIST_LSBS",
    0x65B275E5: "rScenario",  # pc-only
    0x65B5010A: "ASYNC_TASK_STATE",
    0x65B99D72: "CP_2D_BOOLEANS",
    0x65BF8757: "cWpAction_wp_act_ready_loop",  # pc-only
    0x65C0EB4C: "PA_SC_DEBUG_CW_2",
    0x65C13618: "AZ1_LOOPBACK_PATTERN2PHS1",
    0x65C22223: "CCalRenderer",
    0x65C42595: "SQ_CF_BOOLEANS",
    0x65C45465: "ID3DXAnimationController",
    0x65C90FFB: "uOmEvade::cActEvade",  # pc-only
    0x65C95D39: "std::locale",
    0x65CD957A: "cEm32PlEvent_TongueCatch",  # pc-only
    0x65CDEBB7: "PCIE_TXRX_DEBUG_SEQNUM",
    0x65CFCDCC: "SXIFCCG_DEBUG_REG3",
    0x65D0E32A: "CXStorageDownloadWorker",
    0x65D1AF20: "cEm0cActDmgBlow",  # pc-only
    0x65D22F15: "sCollision::cColTree::RegistInfo",
    0x65D34409: "SQ_INSTRUCTION_CF_JMP_CALL_1",
    0x65DB95F8: "sSoundN::StreamVoice::STREAM_COMMAND",
    0x65DBD4BC: "sPad::PAD_FREE",
    0x65DD025D: "LB_DISP1_ALU",
    0x65DE6CEA: "uOmPlate::cActWait",  # pc-only
    0x65DEFC8B: "CP_RT11_SIZE",
    0x65E1805A: "rChain::JointInfo::JOINT_COL_SHAPE",
    0x65E5719F: "uEffectEdit::GEN_RNO_TBL",
    0x65E8FDE6: "_XUSER_PROFILE_SOURCE",
    0x65EADFDE: "_XPROFILE_ACHIEVEMENT",
    0x65EC18CF: "_BASE_MSG_HEADER",
    0x65F2CC26: "rEffectSetData::ESD_SET_MASS_BILLBOARD",
    0x65F87303: "NB_ADAPTER_ID",
    0x65F94498: "_XSTORAGE_UPLOAD_FROM_DIRECTORY_PARAMS_INTERNAL",
    0x65FBD92C: "PA_SC_VIZ_QUERY_STATUS_0",
    0x660090C0: "uOm08b3_S203Elev::cActWaitRise",  # pc-only
    0x660F1F15: "std::nothrow_t",
    0x661BE482: "XONLINE_OFFERING_TYPE",
    0x661EB022: "SQ_GPR_MANAGEMENT",
    0x661EFD06: "_XMBYTE4",
    0x6621B240: "cEm10ActWaitSearch",  # pc-only
    0x6626AB8B: "cEm61ActInvarid",  # pc-only
    0x6627FBCF: "cEm30ActSniff",  # pc-only
    0x662CE08C: "CP_RT3_BADR",
    0x6633A141: "cEm34ActAttack",  # pc-only
    0x6634250E: "rSoundRequestXml::ElementData::MyDTI",
    0x6635C0FA: "PCIE_VC0_CAP_REG2",
    0x66375CBE: "tagDXVA_EMB",
    0x6639183B: "MtCollada::Primitive::MyDTI",
    0x663BAFBB: "PCIE_CAP_LIST",
    0x66429354: "VGT_PERFCOUNTER1_LOW",
    0x6643C44F: "PCIE_VC0_RESOURCE_STATUS",
    0x6644B042: "BIU_FSB_FLUSH_ACK_TIMEOUT",
    0x6647BF7E: "AZ1_MRU_BANK16_DEPTH_MASK",
    0x664EDF75: "_XGUCODE_PASS_DESCRIPTION",
    0x664FE6DA: "_TRACK_DATA",
    0x66544778: "cEm83ActDmgNormalM",  # pc-only
    0x6654EEB9: "CONFIG_CNTL",
    0x66550E87: "PatInterface::SearchFilter",
    0x6659B185: "cFSMOrder::cScenarioArg_eraseActBtn",  # pc-only
    0x665BC6EF: "sCollision::NodeList",
    0x665CAD4D: "cEm30ActDmgRunA",  # pc-only
    0x665EB1F1: "_ACCOUNT_GET_USER_TYPE_REQUEST",
    0x6663877F: "IDirectXFileVtbl",
    0x66647A38: "uEffectVFR::__vftable",
    0x6669304B: "NetworkConnectionStable",
    0x666C185A: "cEm30ActWalkBgn",  # pc-only
    0x66742DD0: "cEm10ActOpenDoor",  # pc-only
    0x6674C77C: "uOma004_Collapse::cActPlRun",  # pc-only
    0x6674F2C1: "sPhysics::RigidBodyParam",
    0x668080E1: "uEffectEdit::Polyline",
    0x6683938E: "cEm44ActRunBgn",  # pc-only
    0x66855F46: "_CERTIFICATE_LOG",
    0x6687433D: "SQ_PERFCOUNTER1_HI",
    0x668B8B3E: "cDemoBase",  # pc-only
    0x668B959D: "uOm090d_Floor::cActMove",  # pc-only
    0x668C3E71: "PatInterface::LayerInfoNtc",
    0x668C912B: "DNameStatus",
    0x668DFE30: "uSynchroAdhesion::MyDTI",
    0x668E3020: "XMACONTEXTINIT",
    0x669119C5: "AZ0_MRU_BANK17_DEPTH_MASK",
    0x6692C556: "CP_INT_ACK",
    0x66948317: "MtCollada::Handler",
    0x669B77DB: "IOC_BSB_SLV_CPL_ARB",
    0x66A3B89A: "CP_RT9_COMMAND",
    0x66A79B72: "CP_RT1_POLL_ADDRESS",
    0x66B0B002: "XNKID",
    0x66B1F99E: "sCollision::cColArrayBP",
    0x66B2FB7F: "RBBM_PERFCOUNTER1_LO",
    0x66B41222: "uPLActor",  # pc-only
    0x66B46D57: "_D3DXWELDEPSILONSFLAGS",
    0x66BB1389: "sCollision::cColArray::__vftable",
    0x66BCDC32: "cEm4502ActDamage",  # pc-only
    0x66BE5D14: "cOmTestAction_om_act_dummy",  # pc-only
    0x66BE678E: "NetworkRanking",
    0x66C0C1A5: "rTexture::TATTR",
    0x66C76EEB: "_FILE_DIRECTORY_INFORMATION",
    0x66CBCE7A: "PA_SC_DEBUG_ITER_4",
    0x66CC0F8D: "_TITLE_DETAILS_REQUEST",
    0x66D35FD1: "cEm41AActMissileUnderGround",  # pc-only
    0x66D69841: "_numberfmtW",
    0x66DEC69E: "lvwparam",
    0x66E15C66: "XAUDIORENDERDRVCLIENT",
    0x66ED95FE: "aS103::cActPreUroBurnt",  # pc-only
    0x66F2EF9F: "D1MODE_VIEWPORT_START",
    0x66F3783C: "NetworkPeerParamMcs",
    0x66F42C5A: "_PixSysMonOpcode",
    0x66F9F62F: "MtProfiler::Profile",
    0x66FAB138: "_XSIGNATURE_CHECK_REVOCATION_REQUEST",
    0x66FF71BC: "cEm30DmgAction",  # pc-only
    0x67004FC4: "cPlAction_pl_act_die_leave_common",  # pc-only
    0x67007A92: "cResource::XmlHandler",
    0x67025A5E: "_DXVA_ProcAmpControlCaps",
    0x67067768: "_D3DDEGREETYPE",
    0x670E4FCC: "rEffect2D::E2D_PARTICLE_POLYLINE",
    0x67125969: "IXAudioSourceEffectVtbl",
    0x6716A2CC: "RTS_BARYC_REF_VTX_Y",
    0x6717FFAE: "RB_PERFCOUNTER3_HI",
    0x671AF10E: "tagWMAFileHdrStateInternal",
    0x671F21DA: "rStartPos",  # pc-only
    0x672BF14E: "CREATE_OWNER_ACCT_REQUEST",
    0x672DD7BA: "ColorArrayX",
    0x67315F74: "CXLiveAsyncTaskInternal::__vftable",
    0x6735152B: "uOm1316_BackupHeli::cEvActOptA_Shoot",  # pc-only
    0x6736D22E: "_EXCEPTION_RECORD32",
    0x6737DC37: "WAVEFORMATEX",
    0x673F08B9: "CConformanceList",
    0x67466676: "PatInterface::GameBinary",
    0x67474BB3: "rEffectList::LIGHT_TYPE",
    0x674C448B: "_CONTENT_HISTORY_ENUMERATE_REQUEST",
    0x674CC0A4: "XAUDIORENDERFXINIT",
    0x6750DF76: "rSoundSource::Descriptor",
    0x6752005F: "uCrossFadeFilter",
    0x675707A6: "XUITimelineCtl",
    0x675B50C3: "sToolBase::MyDTI",
    0x675C6391: "WMVDecInitMTCtlOptionals",
    0x6763891F: "TCF_PERFCOUNTER2_HI",
    0x6763DF20: "_XPROFILE_GAMER_PRESENCE_USER_STATE_VALUE",
    0x67672350: "_P_INVITE_2_MSG",
    0x676C0E24: "cOm08dbEventPL_ActKick",  # pc-only
    0x676D836C: "_FLOAT128",
    0x676DE198: "cPlAction_pl_act_attack_knee_bazooka_turn_r",  # pc-only
    0x6770F33C: "rEffectList::EFL_KEYFRAME_COLOR",
    0x67725630: "cEm32ActAtkWallJump",  # pc-only
    0x67778FEE: "AHCameraElement",  # pc-only
    0x6778DA69: "cEm52ActWait",  # pc-only
    0x677ACD01: "rEffectList::EFL_PARTICLE_PAT_COMMON",
    0x677B0DF6: "cPlAction_pl_act_damage_flash_pl",  # pc-only
    0x677BD269: "uFlatWater",
    0x677C2B55: "NetworkRanking::Board",
    0x677FA72C: "SQ_FETCH_3",
    0x6780A08E: "cEm82DmgLastPinion_PL",  # pc-only
    0x67895D92: "_XDEVICE_DATA",
    0x678DD14A: "_XCONTENT_HEADER",
    0x678DD752: "_FIND_MEDIA_INSTANCE_URLS_RESPONSE",
    0x67935912: "_EX_TITLE_TERMINATE_REGISTRATION",
    0x6793C3C2: "_RUNTIME_FUNCTION_INDIRECT",
    0x6796E047: "uOmHitCheck::cActWait",  # pc-only
    0x679F5B30: "RTS_Z_REF",
    0x679F6715: "uScrVertexBufferQueue",
    0x679F8E88: "uOmElevator::cActGo",  # pc-only
    0x67A14CFF: "std::ios_base::__vftable",
    0x67A714D2: "rScheduler::__vftable",
    0x67A8D462: "MtPreProcessor::MyDTI",
    0x67AA236B: "D3D::MIPPACKINGTYPE",
    0x67AE8BB7: "cOmDoorActOpenClassic",  # pc-only
    0x67B13AE6: "DC_LUT_RW_INDEX",
    0x67B51C22: "XG_MCT::_MCTCOMPRESSION_CONTEXT_HEADER",
    0x67B57113: "uToneMapFilter::TMPASS",
    0x67B87ED5: "MC1_DRAM_CMD",
    0x67B8A60C: "DC_GPIO_XDVODATA_Y",
    0x67BA50D2: "MtPoint",
    0x67BAF48B: "CP_CPU_INT_ACK",
    0x67BB8D76: "AZ0_LOOPBACK_PATTERN2PHS2",
    0x67BD8313: "cEm83PlEvent_PinionOff",  # pc-only
    0x67BE1DDF: "_QUERY_SEARCH_REQUEST",
    0x67BFFA7E: "MATCH_OP",
    0x67C10259: "cTrans::CMD_IPRIM",
    0x67C4E051: "GPUGROUPPRIMTYPE",
    0x67C566D5: "cEm20ActDie",  # pc-only
    0x67CC86FC: "ID3DXFileVtbl",
    0x67D1AD7B: "sApp::MyDTI",
    0x67D523B2: "_DXVA_MBctrl_I_OffHostIDCT_1",
    0x67DABBF8: "rEffect2D::INP_TYPE",
    0x67DDB6F0: "cOmBoatAirAction_om_act_ride_on",  # pc-only
    0x67E3773B: "cTrans::CMD_PRIMCALL",
    0x67EC3EAF: "_SECURITY_DESCRIPTOR",
    0x67EEE15E: "MtCollada::Program",
    0x67F20F40: "cTrans::TAG",
    0x67F5AA95: "NetworkCommunityLive",
    0x68011E48: "TCF_PERFCOUNTER6_HI",
    0x6804E36F: "MC0_DRAM_DATA",
    0x680655EE: "AZ1_LOOPBACK_PATTERN0PHS0",
    0x68073D75: "uOm095e_Kick::cActPlAct",  # pc-only
    0x6808EEB3: "HENHMETAFILE__",
    0x6809C9E9: "GC_PM_STATUS",
    0x680DA4D7: "uOmSwitch::cActSwitchOn",  # pc-only
    0x681673AE: "cEm45ActMove",  # pc-only
    0x6816B494: "MtFCurve::MyDTI",
    0x681AE13A: "cEm32PlEvent",  # pc-only
    0x681F47F9: "sNetworkLibraryXbox::MyDTI",
    0x68212AE3: "_LUID",
    0x68239A91: "CLIPPER_DEBUG_REG05",
    0x6823CF37: "cPlAction_pl_act_jump_broad_3m",  # pc-only
    0x68266520: "cSub",  # pc-only
    0x682D563E: "uOmSwitchPulley::cActPulleyWaitToOn",  # pc-only
    0x6831FA6A: "CLIPPER_DEBUG_REG16",
    0x68330EA8: "_XUSAGE_STORE_REQUEST",
    0x6841101A: "MtPreProcessor::MACRO",
    0x68433743: "uEffectEdit::Light",
    0x6845A748: "_D3DSHADER_COMPARISON",
    0x684F097A: "XGI_ANID_MSG",
    0x684F8418: "tagWMCIndexEntries",
    0x684F8F32: "_XONLINE_REQUEST_THROTTLE_SETTINGS",
    0x6852E1EA: "_SUB_Q_TRACK_ISRC",
    0x6858C12F: "CXDirectoryCrawler",
    0x685BA74D: "_D3DPRESENT_PARAMETERS_",
    0x685D4F64: "NetworkLayer::Sibling",
    0x685FC1D8: "_STRING_LOOKUP_2_REQUEST",
    0x68647F83: "uOm1317_S109_Glass::cActBreak",  # pc-only
    0x68652663: "_D3DDEVINFO_VCACHE",
    0x6867BFB4: "MtCRC",
    0x686D94B3: "cPlAction_pl_act_bump_down",  # pc-only
    0x6870CDEB: "cMaterialStandard::FUNC_LIGHTMAP",
    0x6872E63E: "_D3DSHADER_MISCTYPE_OFFSETS",
    0x6876CD18: "_OBJECT_DIRECTORY",
    0x687EC1F6: "CConformanceInfo",
    0x687F6C8B: "PA_SC_WINDOW_SCISSOR_TL",
    0x688727E9: "XUIMessageFigurePoint",
    0x688A6D53: "_STRING",
    0x688AF19C: "_D3DXSHADER_INSTRUCTIONINFO",
    0x68912001: "MP4DataEntryAliasAtom",
    0x6891CECA: "cEm10ActBack",  # pc-only
    0x68943F38: "cEm42CAction",  # pc-only
    0x689FE960: "PCIE_PERF_COUNT0_MST_C_CLK",
    0x68A0CE3B: "MP4MediaHeaderAtom",
    0x68A527B1: "GpuTempBuffers",
    0x68A69325: "uOm08e3_RuinTrap::cActPlBase",  # pc-only
    0x68A876B1: "ID05_DCP_LB_CHUNK_REQUEST2",
    0x68A878D4: "_XMSG_GAME_INVITE_ANSWER",
    0x68AE1DAA: "_IMAGE_RESOURCE_DIRECTORY_STRING",
    0x68B0F0E3: "uEffect2D::Particle",
    0x68B3C302: "RTS_INITIATOR",
    0x68B69B0A: "CP_PERFCOUNT_SEL",
    0x68B95982: "XAUDIO::CSafeListEntry",
    0x68BA1159: "cOmDeadAction_wait",  # pc-only
    0x68BC0DA9: "_XONLINE_STATS_READ_RESULTS",
    0x68BCB555: "D3D::BeginType",
    0x68BD8268: "MC1_PAD_CAL_STATUS",
    0x68BFE576: "cEmc1ActWait",  # pc-only
    0x68C1E991: "uOm092f::cActBase",  # pc-only
    0x68C29262: "uEffectVFR::ClothZigzag",
    0x68CAEB51: "MtGeomLine",
    0x68CFE739: "cEm10ActDmgGG",  # pc-only
    0x68D4625B: "cLinkUnitEnemy",  # pc-only
    0x68D62F49: "cOmDeadAction_ragdoll",  # pc-only
    0x68D64D52: "SurfaceNumberX",
    0x68DB1856: "PCIE_VC0_RESOURCE_CAP",
    0x68DBB580: "_FXLDATA_CLASS",
    0x68E9B4DA: "_Q_MESSAGE_FLAGS_MSG",
    0x68E9E738: "XONLINE_GET_POINTS_BALANCE_RESPONSE_FLAGS",
    0x68EE8020: "FSB_LX_ERRINJ0_OR",
    0x68F1B76E: "_OBJECT_HANDLE_TABLE",
    0x68F25A4C: "cEm10ActDmgKnee",  # pc-only
    0x68F2DE6E: "_XCONTENT_METADATA_INSTALLER",
    0x68F2FC29: "cEm10ActAtkShieldSpear",  # pc-only
    0x68F42CD5: "MP4TrackExtendsAtom",
    0x68F7F3A0: "BSB_WRAPPER_CNTL0",
    0x68F9B25C: "cOmJeepAction_om_act_ride",  # pc-only
    0x68FA5DE3: "AZ0_EDRAM_INIT",
    0x68FD3152: "lzx_block_type",
    0x68FE9D95: "cFSMOrder::FuncParamFlag",  # pc-only
    0x6901D076: "SQ_EO_RT",
    0x69020EED: "uWater",
    0x6906BD7D: "_D3DSURFACE_PARAMETERS",
    0x690F988C: "MTTASK_STATE",
    0x69105576: "FSB_TLA_TRACE_ARRAY_DATA2",
    0x6910CD30: "SCRATCH_REG2",
    0x691266C8: "D1CRTC_H_TOTAL",
    0x6913E406: "_ACCOUNT_VERIFY_BILLING_INFO_RESPONSE",
    0x69141F04: "std::underflow_error",
    0x691907DB: "AZ1_TOTAL_SAMPLES",
    0x691A2EAE: "_XSTORAGE_DOWNLOAD_TO_MEMORY_RESULTS",
    0x691EB92A: "XHV_INIT_PARAMS",
    0x69225AC9: "BRTINSTANCE",
    0x69285B2C: "CFFT",
    0x692E125C: "uOm0927_Crane::cActWait3Alt",  # pc-only
    0x692F502A: "MC1_SECURE_MEMORY_APERTURE_LOG_BIU",
    0x693294EC: "cEm41AActMissileCatch_PL",  # pc-only
    0x6933A819: "TST_EDGE_DETECT_DATA",
    0x6933D1F1: "rArchive::QUALITY",
    0x6935F0BE: "_DM_GET_INPUT_STATE",
    0x69379BC5: "tagWMVSequenceHeaderInfo",
    0x693CF732: "uOma004_Collapse::cActFailed",  # pc-only
    0x6941DFAC: "uOmClutch::cActWait",  # pc-only
    0x6941E270: "cEm10ActWallWaitR",  # pc-only
    0x6946C2D3: "_XARB_REPORT_STATS_BUNDLE",
    0x6952A56F: "XNetConfigPppoe",
    0x6954FA33: "MtGeomMinkowskiSum",
    0x69585205: "uCoord::__vftable",
    0x695F1615: "cEm22ActAtkCutsDown_PL",  # pc-only
    0x696493F9: "cEm30ActJump1m",  # pc-only
    0x6965FB23: "_TEAM_CREATE_RESULTS",
    0x69678C2E: "CAudioObject",
    0x696A241B: "MC0_TIMING_CNTL_3",
    0x696A8FC8: "MtFile::__vftable",
    0x696C879A: "_SVOD_LEVEL0_HASH_BLOCK",
    0x696CD351: "_XPROFILE_SETTING_READ_REQUEST",
    0x696DA2AC: "std::_Iosb",
    0x69708D8D: "sCollision::cSbcArrayBP",
    0x69721F6F: "MtCollada::Translate",
    0x69789EE9: "_XMHALF2",
    0x697D9024: "XECRYPT_DES3_STATE",
    0x6981D1CB: "XG_MCT::CSimpleEntropyEncoder",
    0x6986EFF3: "rAHCameraXml",  # pc-only
    0x69985A27: "_U32ARRAY",
    0x6999C726: "FSB_LR_CTRL",
    0x699CA091: "rEffectSetDataList::ESD_INDEX",
    0x69A5AF0D: "DC_SURFACE_2_INFO",
    0x69A72932: "uOmTreasureBox::cActBase",  # pc-only
    0x69AB044F: "RTS_EDGE_2_DY",
    0x69ADFADC: "cEm0cActTurn",  # pc-only
    0x69AFBA7E: "VC_PERFCOUNTER1_LOW",
    0x69B22E52: "uEffectVFR::PTCL_LIFE_RNO_TBL",
    0x69BEFE4A: "sEffectBase::FilterControl",
    0x69C2228D: "uCloth::Chain::MyDTI",
    0x69C42EFF: "cOmDoorActBang",  # pc-only
    0x69C74EDF: "rMovie::__vftable",
    0x69CD3269: "cUnit::BEFLAG",
    0x69D0CEB2: "cPlAction_pl_act_item_use_partner_first",  # pc-only
    0x69D65E91: "_Q_SEND_MESSAGE_MSG",
    0x69D8EA7A: "IXMAContext",
    0x69DB4AC8: "tWAVEFORMATEX",
    0x69E0ECC8: "XAUDIO::XAUDIOVOICEFXCTX",
    0x69E1B974: "uOm090c_BeltShutter::cActPlHit",  # pc-only
    0x69E3BC34: "_XMEDIA_XMV_CREATE_PARAMETERS",
    0x69EA7F87: "FORMATINFO",
    0x69EEF54F: "cEm32ActMountHold",  # pc-only
    0x69EF8CC1: "PatInterface::CircleInfoNtc",
    0x69F92FA7: "RB_BC_AZ_CRC_MASK",
    0x69FEE9F7: "FSB_TLA_TRACE_ARRAY_ADDR",
    0x6A000349: "rEffectSetData",
    0x6A008308: "_ATA_PASS_THROUGH",
    0x6A02F6C2: "_D3DSWAP_STATUS",
    0x6A03110B: "_D3DXSHADER_CONSTANTINFO",
    0x6A05864E: "_UCODE_DEFINITION_TABLE_ALU_CONSTANT_RECORD",
    0x6A06A65D: "TPC_DEBUG0",
    0x6A0837D2: "MP3SI",
    0x6A092764: "sPrim::FUNC_PRIM_BILINEAR",
    0x6A19EF50: "PCIE_PORT_DATA",
    0x6A1B7576: "TP1_CHECKSUM_PIXEL_3",
    0x6A1E654A: "PCIE_PERF_CNTL_MST_R_CLK",
    0x6A22AE28: "cEm32ActDmgDown",  # pc-only
    0x6A276FCF: "cEm10ActSideStep_R",  # pc-only
    0x6A2C6DAE: "SX_PERFCOUNTER0_SELECT",
    0x6A2EC243: "uSpotLight",
    0x6A323E62: "XShaderPDBBuilder",
    0x6A324977: "cEm20ActHoldTrapCeil",  # pc-only
    0x6A33EF42: "ERRCORRECTION",
    0x6A351631: "XUIMessageSetScrollEndState",
    0x6A366911: "_MM_STATISTICS",
    0x6A3B93B1: "sCollision::cColArrayBP::MyDTI",
    0x6A3F0E08: "_LSP_ENUMERATE_REPLY",
    0x6A3F623E: "AZ0_MRT_STATE_DWORD2",
    0x6A466862: "DC_GPIO_XDVODATA_MASK",
    0x6A48215A: "rSoundRandomXml::ElementData",
    0x6A494066: "RETRACETICKET",
    0x6A4F7FE7: "cEm82PlEvent",  # pc-only
    0x6A50CDE6: "cFSMOrder::FuncParamNpcIgnoreUnit",  # pc-only
    0x6A557C6D: "_TYPED_MEDIA_URL",
    0x6A55D2A0: "_D3DXMESH",
    0x6A5A273F: "uOm090c_BeltShutter::cActMove",  # pc-only
    0x6A5A7480: "_XUSER_STATS_VIEW",
    0x6A5A8D61: "uOmJeep::cActPlDead",  # pc-only
    0x6A5E6CC0: "cOmCoopBoxAction_om_act_wait",  # pc-only
    0x6A636A5D: "cPositionEvaluationSectorFromPos",  # pc-only
    0x6A671CFB: "DC_PERFCOUNTER1_HI",
    0x6A67AE18: "sCamera::Viewport::__vftable",
    0x6A6CB8A1: "CP_CPU_INT_CNTL",
    0x6A701917: "uEffectEdit::BillboardKeyframe",
    0x6A762635: "rEffectList::ROT_RESET_FLAG",
    0x6A79375A: "aStageBase::cStageAct",  # pc-only
    0x6A7B61EC: "_SINGLE_LIST_ENTRY",
    0x6A7CEE80: "AZ0_LOOPBACK_PATTERN0PHS3",
    0x6A7F1378: "uTextureBlend",
    0x6A84B324: "D3D::CVertexShader::PassData",
    0x6A85AFB6: "rEffectList::EFL_MOVE_PATH_STRIP",
    0x6A889046: "XML_ELEMENT",
    0x6A8C8E5A: "rChain::ChainInfo",
    0x6A8D6772: "_FPQ64",
    0x6A8E4940: "DCCG_DEBUG",
    0x6A9762F0: "cPlAction_pl_act_walk",  # pc-only
    0x6A98E2D7: "cAIFSM::ParamBitNo32",  # pc-only
    0x6AAB2CF7: "rVibration::VIB_TYPE",
    0x6AAD56F6: "XAUDIO::CReverbEffect::__vftable",
    0x6AB05B91: "uOmS508_Break::cActWait",  # pc-only
    0x6AB61A89: "uOceanWater",
    0x6AC4337C: "_XAM_CACHE_FILE_TYPE",
    0x6AC4665E: "_XAUDIOPIXCOUNTER",
    0x6AC600D3: "PIX_D3D_GENERAL_COUNTERS",
    0x6AC8E522: "_HV_IMAGE_EXPORT_TABLE",
    0x6ACE8893: "NetworkSessionManager",
    0x6AD39676: "uOm0201_Piano::cActReady",  # pc-only
    0x6AD6B0E0: "cEm32ActMountFinish",  # pc-only
    0x6AD7B16E: "sItem::ITEM_DROP_INFO",  # pc-only
    0x6ADC5727: "_DVD_AP25_CHALLENGE_TABLE_HEADER",
    0x6ADE2A32: "cEm30ActNeckBite",  # pc-only
    0x6AE19477: "uOmClutch::cActPlEscape",  # pc-only
    0x6AE27F28: "uMotionCamera",
    0x6AE49691: "WMVDecInitMTCtl",
    0x6AE75188: "SinCosTable",
    0x6AE94A15: "_CDROM_DISK_DATA",
    0x6AEBB5BC: "NetworkLayerPat",
    0x6AEF520A: "DNameNode",
    0x6AF3E873: "uEffectEdit::PrimModel",
    0x6AF6C1BD: "cHit",  # pc-only
    0x6AFA2AA9: "rEffect2D::ENTRY_TYPE",
    0x6AFC11A7: "SCLK_G_DCP_CNTL",
    0x6AFDC523: "cEm84ActHang_Fire",  # pc-only
    0x6B0373F6: "rSoundCurveSet::List",
    0x6B066597: "TP0_DEBUG",
    0x6B06C0D7: "cTrans::CMD_CLEAR",
    0x6B0AF88E: "sVibration::VibControl::VIB_RNO",
    0x6B0F0748: "uPLActorEm84",  # pc-only
    0x6B15FD20: "rBioTree::Node",  # pc-only
    0x6B19E3EB: "VC_PERFCOUNTER3_HI",
    0x6B25D679: "TCO_STALLS_DEBUG",
    0x6B2C7ED0: "cOmCoopGateAction_om_act_opened",  # pc-only
    0x6B301E10: "rEffectList::COLL_TYPE",
    0x6B304417: "cEm46ActAttackA_Pl",  # pc-only
    0x6B32FC3F: "cMaterialStandard::FUNC_LIGHTING",
    0x6B36BB8F: "IDirectXFileData::__vftable",
    0x6B378389: "D1MODE_UNDERFLOW_STATUS",
    0x6B388117: "tagEMB_PassContext",
    0x6B38CFE6: "cTrans::MyDTI",
    0x6B39F812: "FSB_TLA_COMPR_CARE_MASK2",
    0x6B3B4FE9: "VGT_CRC_SQ_DATA",
    0x6B3D6907: "cEm10ActBackStep",  # pc-only
    0x6B42CB1B: "D1SCL_CRC_CURRENT",
    0x6B42D2FE: "NetworkLayer::MemberSearch",
    0x6B46D1FF: "_DXFILELOADMEMORY",
    0x6B47A2BB: "TP0_CHECKSUM_PIXEL_1",
    0x6B4831DF: "NetworkAddress",
    0x6B4C3512: "_WMVIMAGE_EFFECTS",
    0x6B4EA458: "uToneMapFilter::GLARE_TYPE",
    0x6B5554A6: "uEffectVFR::Culling",
    0x6B58A187: "CP_STATE_DEBUG_DATA",
    0x6B5CF4F4: "cFSMOrder::FuncParamPersonalEv",  # pc-only
    0x6B5D4FC7: "sMouse",
    0x6B61ABA2: "XGENDIANTYPE",
    0x6B63B5F3: "AZ1_MRT_STATE_DWORD0",
    0x6B6A6C43: "_FXLPARAMETER_DESC",
    0x6B6C205E: "PIX_WRITE_GPU_CAPTURE",
    0x6B72EB09: "MtFloat3",
    0x6B74D7B6: "ID3DXInclude",
    0x6B792EAB: "uSpotShadow",
    0x6B7A3687: "cEm41ArmAction",  # pc-only
    0x6B81BA7C: "CP_RT8_REFERENCE",
    0x6B84B561: "cEm62ActDieIce",  # pc-only
    0x6B8EAD4C: "HZ_PERFCOUNTER1_SELECT",
    0x6B901732: "tagBITMAPINFOHEADER",
    0x6B90AD57: "PA_SU_POLY_OFFSET_FRONT_OFFSET",
    0x6B9271FD: "uEm80EventPL_ActPre",  # pc-only
    0x6B92C1FE: "uOm08db::cActWait",  # pc-only
    0x6B947987: "XUIMessageSoundMute",
    0x6B957D14: "std::locale::id",
    0x6B9950C6: "_XSIGNATURE_VERIFY_RESPONSE",
    0x6B99ADFE: "CP_RT10_COMMAND",
    0x6BA15571: "GC_PMI_DATA",
    0x6BA2510F: "cEm44ActTurn",  # pc-only
    0x6BA413A4: "_Q_DEQUEUE_MSG",
    0x6BA45F99: "GPU_CONTROLPACKET",
    0x6BAF6AAA: "MtPreProcessor::Include",
    0x6BB0C3F2: "_XGTEXTURE_DESC",
    0x6BB0DAF6: "GC_STATUS",
    0x6BB2E5EB: "uOmS705ceil::cActFall",  # pc-only
    0x6BB41C1E: "_WMVGetDataCallbackHandler",
    0x6BB9C962: "_XNET_LOGON_USER",
    0x6BBD13B7: "rClothXml::MyDTI",
    0x6BBD254D: "_KAPC",
    0x6BBD9B4E: "RBBM_PERFCOUNTER1_HI",
    0x6BBEA154: "CCalReadAheadFileStream::CreateParameters",
    0x6BC32677: "_CERTIFICATE_REVOCATION_DATA",
    0x6BC3C7F7: "_XONLINE_USER_TEAM",
    0x6BC94C3F: "DMIF_STATUS",
    0x6BCB9B7F: "cEm20ActAtkBack",  # pc-only
    0x6BCE241C: "rEffectList::EFL_MOVE_PATH_KEYFRAME",
    0x6BD3BE98: "IOC_INVALID_AP_BSB",
    0x6BD6231E: "PA_SU_PERFCOUNTER3_HI",
    0x6BD62F6E: "cFSMOrderPawn::FuncParamMotion",  # pc-only
    0x6BDD7E0D: "rEffectAnim::SEQ_PAT",
    0x6BDE461D: "cPlAction_pl_act_turn_l",  # pc-only
    0x6BE5697F: "CP_RT12_MASK",
    0x6BE719E3: "TCO_QUAD1_DEBUG0",
    0x6BEB36A6: "cEm83ActDmgKnockDown",  # pc-only
    0x6BEF2A89: "DepthArray",
    0x6BF5B6BF: "MC0_SECURE_MEMORY_APERTURE_SIZE",
    0x6BF5BB41: "cEm8cActStageChange",  # pc-only
    0x6BF754FB: "cWpAction_wp_act_gunemp_fire",  # pc-only
    0x6BF9A2FD: "CAacDecoderStaticChannelInfo",
    0x6C078EAB: "uVolumeNoiseFilter::MyDTI",
    0x6C09F6F0: "MtRegistry::STORAGE_TYPE",
    0x6C0A45E4: "D3D::XpsObject",
    0x6C0B0C1A: "cFSMOrder::FuncParamApplySound",  # pc-only
    0x6C0CD545: "GPUCOLORARRAY",
    0x6C0D3FF4: "PA_SC_MPASS_PS_CNTL",
    0x6C11428B: "_DXVA_ProcAmpControlBlt",
    0x6C12EF2A: "_cpinfoexA",
    0x6C17303D: "_GENERIC_MAPPING",
    0x6C215151: "_XPROFILE_ACTION_AUTO_AIM_OPTIONS",
    0x6C240E9F: "_P_TEAM_DELETE_MSG",
    0x6C25FEA0: "D3D::MiniMicrocodeBuilder",
    0x6C2FFDFD: "TileDepthFunc",
    0x6C30658C: "_UCODE_R500UCODE_COMMON",
    0x6C32DFEB: "PACKET_PROCESSOR",
    0x6C34C1B8: "sCollision::ScrColInfoGetAreaPoly::MyDTI",
    0x6C3DFD5E: "uColorCorrectFilter::Corrector::TYPE",
    0x6C43605D: "cEm63ActErase",  # pc-only
    0x6C43B502: "_KTRAP_FRAME",
    0x6C54A1E0: "uOmS109_Driver::cActCrash",  # pc-only
    0x6C5A082D: "XConfigStaticSettings",
    0x6C619332: "MtMemory",
    0x6C6C1E11: "_DVD_XGD2_DISC_AUTH_RESULT_HCRT_HEADER",
    0x6C6C5C2A: "tagBITMAPINFOHEADER_BITFIELDS",
    0x6C6D31C4: "ip_mreq",
    0x6C6F21AB: "_auencInputParams",
    0x6C735701: "SB_REGPROG_INF",
    0x6C7ABCF7: "XUIMessageInit",
    0x6C840B0A: "cEmc6Action",  # pc-only
    0x6C84270F: "rEffectList::EFL_KEYFRAME_F32",
    0x6C85C4BD: "NetworkSessionManager::Property",
    0x6C8B409D: "cFSMOrder::FuncParamBool",  # pc-only
    0x6C8CE045: "RTS_Z_DX_DY_LSBS",
    0x6C8D3719: "cEmc0ActOff",  # pc-only
    0x6C8D54CB: "XAUDIO::CSourceStream",
    0x6C9E5ABA: "cPositionFilterRangeAroundKeepPos",  # pc-only
    0x6CA056DB: "RBBM_SKEW_CNTL",
    0x6CA188FF: "ID3DXBaseMesh",
    0x6CA6BFDE: "D3DXShader::_D3DCOMPONENT_TYPE",
    0x6CACC996: "_XMDHENN3",
    0x6CAF1861: "cEm60ActWalk",  # pc-only
    0x6CB12FA4: "uBloomFilter::MyDTI",
    0x6CB1C565: "uOmCoopTreasure::cActPlOpening",  # pc-only
    0x6CB3559B: "MtCalculator",
    0x6CB76BF5: "uEffectEdit::MoveAddKeyframe",
    0x6CBCD457: "_QUERY_ADD_REQUEST",
    0x6CBD8889: "VGT_GRP_PRIM_ORDER",
    0x6CC07D90: "BIT_BUF",
    0x6CC4234C: "_XGD2_GET_TEST_INFO",
    0x6CC5F6B1: "_D3DSAMPLERSTATETYPE",
    0x6CC76A1B: "rSoundDirectionalCurveXml::Curve",
    0x6CC7DC60: "sParameter::ATK_EX_PARAM_STRIKE_STRUCT",  # pc-only
    0x6CCB536A: "cNetEm50",  # pc-only
    0x6CCF1552: "uOmExplosive_Fell::cActLetFall",  # pc-only
    0x6CD0907A: "DC_LUTA_BLACK_OFFSET_BLUE",
    0x6CD30125: "MP4DataEntryAtom",
    0x6CD544C5: "D1GRPH_SURFACE_OFFSET_Y",
    0x6CD749D1: "rEffectStrip::PARTS_PARAM",
    0x6CD93391: "cNetEm43",  # pc-only
    0x6CDEDD58: "NetworkCommunityLive::moveEditFriendList::__l3",
    0x6CDF3C95: "ROM_SIMD_PIPE_DISABLE_REGISTER",
    0x6CEC06C1: "PIX_INDEX_TYPE",
    0x6CEE53CF: "XConfigUserSettings",
    0x6CF3A53D: "_SUBSCRIPTION_ENUMERATE_REQUEST",
    0x6CF49590: "_XEX_VITAL_STATS",
    0x6CF72E4E: "sPad::MyDTI",
    0x6CFD8988: "cAIPathCostManager::NodeCostJobInfo",  # pc-only
    0x6CFDF860: "XAMTIMEFORMAT",
    0x6CFE9E6A: "D1GRPH_COLOR_MATRIX_COEF_1_2",
    0x6D04FDB7: "CP_RT_POLL_INTERVAL",
    0x6D063118: "MtPreProcessor::Include::MyDTI",
    0x6D0CEB84: "CMotionVector",
    0x6D0EFF97: "DC_LUTA_WHITE_OFFSET_BLUE",
    0x6D1382E5: "INPUTSRCINFO",
    0x6D16B212: "MC1_WR_STR_DLL_1",
    0x6D1CD990: "PIX_LOG_TYPE",
    0x6D26D7C2: "_XCONTENT_METADATA_INSTALLER_TITLE_UPDATE",
    0x6D2B331B: "BlockNum",
    0x6D2C9D17: "uOm08db::cActFall",  # pc-only
    0x6D2F2D98: "XAUDIO::CSpinLock",
    0x6D33C412: "XVOICE_OBJECT",
    0x6D33D8BD: "TP0_CHICKEN",
    0x6D3557F7: "MtXmlWriter::SCOPE",
    0x6D384EE8: "cEm3402ActWait",  # pc-only
    0x6D3A576C: "_D3DTEXTUREADDRESS",
    0x6D41DEE0: "_XSTORAGE_UPLOAD_REQUEST",
    0x6D450823: "MC1_TUNING_1",
    0x6D510C70: "cOmBoltAction",  # pc-only
    0x6D524066: "sCollision::SbcInfoMin",
    0x6D5251C4: "RB_HSIO_INTERFACE_ALIGNER_VALUE",
    0x6D5AE854: "rEffectList",
    0x6D614661: "IOCPERFEVENT",
    0x6D699C20: "CODECGETMOREDATACONTEXT",
    0x6D6CF9D0: "XUIMessageFigurePointIndex",
    0x6D6DCF71: "_HCR",
    0x6D6E91DC: "rEffectList::EFL_PARAM_CLOTH_ZIGZAG",
    0x6D6FF6E8: "cOma016ActWait",  # pc-only
    0x6D70724D: "std::_Container_base",
    0x6D711BD1: "CP_RT11_MASK",
    0x6D7143B0: "cEm32TongueActDamage",  # pc-only
    0x6D76D40F: "TileStencilFunc",
    0x6D76E7A6: "_KDPC",
    0x6D77BDF4: "ID3DXEffect::__vftable",
    0x6D7D9D60: "BIST",
    0x6D8B1D81: "aS109::cActPlBase",  # pc-only
    0x6D8BEE01: "cEm10ActAtkFatHandSwing",  # pc-only
    0x6D8D0BE9: "cPositionFilterDoughnutAroundAwayPos",  # pc-only
    0x6D8D84E9: "PA_CL_POINT_X_RAD",
    0x6D8EADD3: "HUDSCENE",
    0x6D8EEBB3: "cOmWindowAction_bang",  # pc-only
    0x6D8F7147: "CP_ME_PS_EVENT_DATA_SWM",
    0x6D8FFC44: "cTrans::VSTREAM",
    0x6D93B5DB: "GPUCONSTANTID",
    0x6D963507: "sParameter::LEVEL_PARAM_S",  # pc-only
    0x6D96900F: "ID09_LUT_DATA_R",
    0x6D96DAF2: "rSoundRequest::SOUND_REQUEST_EQ_CATEGORY",
    0x6D97BF67: "cOmCoopBoxAction_om_act_shake",  # pc-only
    0x6D9A6F48: "CXuiCachingModule",
    0x6D9C620C: "CCalBase::FILTER_TYPE",
    0x6D9D0BC7: "cEm66ActWaitWater",  # pc-only
    0x6DA0F9E9: "_DVD_XGD2_DRIVE_AUTH_RESULT_CODE",
    0x6DA6081E: "_XASSET_ENUMERATE_REQUEST",
    0x6DA625E1: "_PASSPORT_GET_MEMBER_NAME_REQUEST",
    0x6DA7C2FD: "cEm20ActDmg",  # pc-only
    0x6DAAC26A: "HWND__",
    0x6DAC868D: "_MIGRATE_XBOX1_USER_REQUEST",
    0x6DB0DB90: "cEm30ActDmgToDie",  # pc-only
    0x6DBD21EC: "rMovie::MyDTI",
    0x6DBFC03B: "uColorBar",  # pc-only
    0x6DC15A18: "cPlAction_pl_act_wall_stick_wait",  # pc-only
    0x6DC5A452: "CP_INT_STATUS",
    0x6DC817BA: "uOm095c_Break::cActBreak2",  # pc-only
    0x6DCF62FD: "_ACCOUNT_TROUBLESHOOT_REQUEST",
    0x6DCF7862: "cEm3403Action",  # pc-only
    0x6DD0BE85: "_XPERSISTENTMEMPARAMS",
    0x6DD3C136: "rEffectSetData::ESD_MOVE_ADD",
    0x6DD5A341: "_FSINFOCLASS",
    0x6DDFBD37: "rEffectSetData::FILTER_TYPE",
    0x6DE40EC2: "XECRYPT_DH",
    0x6DE529E5: "aS700::EvAct_Window",  # pc-only
    0x6DE68D24: "cLinkUnitFSM",  # pc-only
    0x6DEAB4B6: "AHShapePolygon::Vector",  # pc-only
    0x6DF200CC: "sPhysics::Constraint::MyDTI",
    0x6DF54A3A: "rArchive::ARCHIVE_HDR",
    0x6DF8B0F1: "uBlurFilter",
    0x6E00F211: "uOmDive::cActDive",  # pc-only
    0x6E01F65E: "_DXVA_VideoSample",
    0x6E042EBB: "uSpotLight::ORDER",
    0x6E043C77: "D1GRPH_Y_END",
    0x6E04461E: "cEm20ActEndTrapCeil",  # pc-only
    0x6E0A7787: "rSoundCurveXml::MyDTI",
    0x6E0BC6D0: "cEm34ActErase",  # pc-only
    0x6E0D123D: "GPUTEXTUREFETCHOP",
    0x6E1556FD: "sLightLinker::uAnimLight",  # pc-only
    0x6E175579: "sVibration::PadVibration::__vftable",
    0x6E19EDDE: "_XONLINE_ATTRIBUTE",
    0x6E20B185: "tUNCACHE_CTL",
    0x6E20EA8E: "RB_ALPHA_REF",
    0x6E24C894: "cNetEmc2",  # pc-only
    0x6E25A7AE: "NetworkRandom::__vftable",
    0x6E25D54D: "rEffect2D::COLOR_FLAG",
    0x6E27F84F: "_XONLINE_CACHE_CFFILE",
    0x6E29D860: "D3D::SamplerStateInit",
    0x6E2A4A97: "_INSTALLER_METADATA_TYPE",
    0x6E2B19F7: "std::ctype_byname",
    0x6E305241: "TP1_CNTL_STATUS",
    0x6E305F8D: "CGM_MC0_IO_CNTL",
    0x6E348C59: "_FILE_XCTD_COMPRESSION_INFORMATION",
    0x6E3C77E5: "D1CRTC_FRAME_COUNT_CONTROL",
    0x6E3E36CE: "FSB_TX_PMCTRL_OR",
    0x6E430E5C: "cEm84ActDmgGetup",  # pc-only
    0x6E48E3EB: "XAUDIOFXUNREGISTER",
    0x6E4BFD2F: "MtGeomCone::MyDTI",
    0x6E4CA766: "uOmJoke::cActMove",  # pc-only
    0x6E4CB122: "cTrans::CMD_RT",
    0x6E5571D2: "_XSESSION_REGISTRANT",
    0x6E55AE49: "uOm1303_S109_Truck::cActOverturn",  # pc-only
    0x6E5AAF88: "_D3DSTENCILOP",
    0x6E5CA357: "XHUDOPENSTATE",
    0x6E60F7B4: "uActorModel::MyDTI",
    0x6E6158C1: "MtCollada::Primitive::TYPE",
    0x6E61B3FC: "_D3DVIEWPORT9",
    0x6E707930: "NetworkStorage::__vftable",
    0x6E73764C: "sEventPlayer",  # pc-only
    0x6E759866: "VGT_DEBUG_DATA",
    0x6E78E582: "rEffect2D::LIFE_TYPE",
    0x6E795483: "SEQUENCE_INFO",
    0x6E7D0929: "SCRATCH_REG6",
    0x6E7EF219: "std::logic_error",
    0x6E806471: "_XNET_LOGON_TITLE",
    0x6E8320DF: "RENDERERMSGINFO_SETIMAGESIZE",
    0x6E83499B: "CXUpdateDownload::REFRESH_LICENSE_RESPONSE_BUFFER",
    0x6E86471A: "RTS_Z_MAX",
    0x6E8C1D03: "cEmc2ActWhip",  # pc-only
    0x6E8E98EB: "UVBASE_CALLBACKUSERTOVOICECHATPARAM",
    0x6E90399D: "rEffectList::EFL_PARTICLE_MASS_BILLBOARD",
    0x6E917E98: "CCalBase::CODEC_TYPE",
    0x6E93C938: "TP2_CHECKSUM_PIXEL_1",
    0x6E93DFA1: "TCF_PERFCOUNTER1_LOW",
    0x6E953D08: "FSB_LX_DEBUG_LO_AND",
    0x6E99611F: "SurfaceNumber",
    0x6E9F47C9: "cTrans::VertexDecl",
    0x6EA0D355: "MP4CalInputStreamRecord",
    0x6EA4750C: "cEm84ActAppear",  # pc-only
    0x6EA4EB87: "uOma00f_UroPunch::cActPlEvade",  # pc-only
    0x6EB1169E: "_PIXCOUNTERREPORT",
    0x6EB15EF6: "_FXLPASS_DESC",
    0x6EB5A33D: "_XSTORAGE_ACCESS_TOKEN_WRITE",
    0x6EB82033: "D1GRPH_COLOR_MATRIX_COEF_2_2",
    0x6EBA0A40: "NetworkMutex",
    0x6EBC2BBD: "_XUIOBJ",
    0x6EC0A749: "cPlEventAct_stop",  # pc-only
    0x6EC16599: "cEm43ActCatchKill_Pl",  # pc-only
    0x6EC68AB6: "TCF_PERFCOUNTER11_SELECT",
    0x6EC7DE6F: "NetworkSessionStable::ConnectionParameter",
    0x6ECAAC78: "BSB_DEBUG_CNTL",
    0x6ECDFA04: "_FB_ENUM_REVIEWS_RESPONSE",
    0x6ED02D12: "cTrans::Technique::VS",
    0x6ED75BD3: "AZ0_COPY_STATE_DWORD0",
    0x6EDCED8E: "_XDEVICERENAMEPARAM",
    0x6EDE2777: "sExceptionHandler::__vftable",
    0x6EDF3CF4: "NetworkUnitPacket",
    0x6EE51D3C: "CP_ME_VS_EVENT_DATA",
    0x6EE5F4E3: "cEm10ActAtkTorchRanda",  # pc-only
    0x6EE6E71A: "cEm8eActRun",  # pc-only
    0x6EECBC9F: "uOm0934::cActWait",  # pc-only
    0x6EECFAA5: "SQ_INSTRUCTION_ALU_0",
    0x6EF8D40D: "MP4DataEntryURNAtom",
    0x6EFACFC2: "cPlAction_pl_act_knife_ready_end",  # pc-only
    0x6EFF2609: "NetworkSessionManagerLive::PropertyMapSessionBinary",
    0x6F019558: "cEm30ActNeckBiteMissTH",  # pc-only
    0x6F0714B2: "_DM_ODD_MOUNT_DATA",
    0x6F08F4C3: "EP_REVISION_ID",
    0x6F0D61EC: "cEm32ActCornerDown",  # pc-only
    0x6F0DAA0B: "rEffectSetData::ESD_MOVE_ADD_COLL",
    0x6F0DEC00: "_EXCEPTION_REGISTRATION_RECORD",
    0x6F0F871F: "uOm090d_Floor::cActAuto",  # pc-only
    0x6F127E1E: "cEm45ActPoleAtk",  # pc-only
    0x6F16D3CF: "cTrans::Technique::SHADERPARAM",
    0x6F186250: "_SUBSCRIPTION_ENUMERATE_RESPONSE",
    0x6F1BC6D3: "RecordResourceType",
    0x6F1E0FCA: "CCalBase::MEDIA_TYPE",
    0x6F200F8F: "_XMUSHORT4",
    0x6F23D81D: "AZ1_LOOPBACK_TRANSMIT_COUNT",
    0x6F2527AD: "TCM_PERFCOUNT_SELECT",
    0x6F282365: "cOmDoorActBreak",  # pc-only
    0x6F29AEDA: "GenericSampleEntryAtom",
    0x6F29BAC1: "SBR_DECODER_INSTANCE",
    0x6F2EF66E: "uOm1303_S109_Truck::cActBase",  # pc-only
    0x6F321AE6: "_D3DSHADER_PARAM_REGISTER_TYPE",
    0x6F3552F5: "cPlAction_pl_act_climb_cliff",  # pc-only
    0x6F389C42: "ID3DXEffectPoolVtbl",
    0x6F3972B4: "rAIFSM::ParamBitNo32",  # pc-only
    0x6F3B3390: "XDVO_STRENGTH_CONTROL",
    0x6F3BF2D1: "MtHalf4",
    0x6F3D0EF4: "XECRYPT_HMACMD5_STATE",
    0x6F416325: "_TEAM_MEM_ENUM_RESULTS",
    0x6F475C56: "cEm10ActWallAimR",  # pc-only
    0x6F4E57BD: "cEm10ActAtkKick",  # pc-only
    0x6F4E5E88: "CLIPPER_DEBUG_REG01",
    0x6F4F1117: "uColorSpaceFilter::MyDTI",
    0x6F4FD5C7: "EHExceptionRecord",
    0x6F5589AE: "sSoundN::SeEntry",
    0x6F591E0C: "_PASSPORT_SESSION_TOKEN",
    0x6F5A9CCD: "uMovie::STATUS",
    0x6F5C3E73: "CLIPPER_DEBUG_REG12",
    0x6F5C7D88: "rStartPos::Info",  # pc-only
    0x6F5E90AC: "_audecInitParams",
    0x6F5F080E: "cOmTestAction_om_act_damage",  # pc-only
    0x6F6623C9: "_RUNTIME_FUNCTION_TYPE",
    0x6F685811: "cEm20ActAtkCatch",  # pc-only
    0x6F6A7D6B: "SQ_PS_CONST",
    0x6F6B6A1D: "PCIE_LC_CNTL",
    0x6F6D8C81: "Exporting",
    0x6F6F6347: "MtCollada::LookAt::MyDTI",
    0x6F7006EE: "cEm10ActAtkPlagaEatBackStart",  # pc-only
    0x6F740D63: "rVibration::VIB_OPTION_FLAG",
    0x6F77C78F: "_XMDEC4",
    0x6F7A4A04: "D1GRPH_COLOR_MATRIX_COEF_3_2",
    0x6F861650: "MtFile::TIME",
    0x6F8772E9: "DecodeStatus",
    0x6F88AF33: "XUIMessageSizeChanging",
    0x6F910565: "AHEffectRain",  # pc-only
    0x6F95017D: "RB_PERFCOUNTER1_LOW",
    0x6F973893: "uTVNoiseFilter::trans::__l15::SCREEN_VERTEX",
    0x6F97939E: "FSB_TX_TERST_OR",
    0x6F9ACD70: "XAUDIOSRCALGORITHM",
    0x6F9DABEE: "rGridEnvLight",
    0x6F9DE022: "_DXVA_ProcAmpControlProp",
    0x6F9FC3AF: "FSB_TR_DEBUG_AUX",
    0x6FA49E10: "MtSerializer::XmlHandler::Context",
    0x6FA96A27: "_CEA861_SPEAKER_ALLOCATION",
    0x6FAA4710: "DRMINFO",
    0x6FAC52A6: "CArgument",
    0x6FACAECE: "rEffectList::EFL_PARTICLE_POLYGON",
    0x6FADD4FD: "cOma016EmEvent",  # pc-only
    0x6FAF85E8: "IDirectXFileSaveObject",
    0x6FB24877: "CXMsgSendBase",
    0x6FB318C1: "D3D::CBuilder",
    0x6FB56E48: "PCIE_PERF_CNTL_EVENT1_PORT_SEL",
    0x6FBB7FED: "_LARGE_INTEGER",
    0x6FBD2F16: "RB_HSIO_DLL_ADJ1",
    0x6FBF1D24: "cEm42ActDeathBeat",  # pc-only
    0x6FC260C8: "uIdTitle01",  # pc-only
    0x6FC48424: "rEffectSetData::ESD_EXT_LENS_FLARE",
    0x6FC5354C: "PIX_BACKDOOR_STREAM_REQUEST",
    0x6FC8326E: "BSB_WRAPPER_PRBS23_BITCNT1",
    0x6FCCAE43: "MtCollada::Rotate::MyDTI",
    0x6FCF1EF5: "TP3_CHECKSUM_PIXEL_3",
    0x6FD6A146: "StencilOp",
    0x6FD6ADEF: "_XONLINE_MUTELIST_INTERNAL",
    0x6FD7EDDE: "LOOPF_FLAG",
    0x6FDF7630: "ED_CG_CLK_CNTL",
    0x6FE1DC91: "_D3DXSHPRTSPLITMESHVERTDATA",
    0x6FE5FE4B: "ID3DXMatrixStack",
    0x6FE85FF5: "cEm40ActTurn",  # pc-only
    0x6FE9208D: "MP4VisualSampleEntryAtom",
    0x6FE950B2: "MP4FileMappingInputStreamRecord",
    0x6FF0919B: "MtPreProcessor::Include::TYPE",
    0x6FF56E8C: "cEm10ActWalkNoMotion",  # pc-only
    0x6FF8E5B5: "BIU_INT_BAD_IOC_WRITE_ADDR",
    0x6FFF63E1: "PARSERTYPE",
    0x70016EE5: "sUnit::MyDTI",
    0x7003CE2A: "cEm42ActWait",  # pc-only
    0x700409E3: "_FXLSAMPLERSTATE",
    0x7005E578: "uChain::JointWork",
    0x700A9B51: "cActionButton",  # pc-only
    0x700F696D: "XAUDIO::CPacketList",
    0x700F96DC: "XAUDIO::CThread::__vftable",
    0x7010C9CF: "sParameter::ATK_EX_PARAM_THROW_STRUCT",  # pc-only
    0x70116070: "_PAM_SET_NOTIFICATON_HANDLER_EX",
    0x701904CC: "FSB_TLA_TRACE_ARRAY_DATA1",
    0x70195364: "MC0_WR_STR_DLL_1",
    0x70199C8A: "SCRATCH_REG1",
    0x7019A20C: "_D3DRENDERSTATETYPE",
    0x701D5D68: "sResource",
    0x70278008: "MP4ShadowSyncAtom",
    0x70282481: "cTrans::CMD_RS",
    0x702A7005: "cEm30ActDmgZuri",  # pc-only
    0x702DCB13: "MC1_INTERRUPT_MASK",
    0x702E4456: "_D3DXF_FILELOADMEMORY",
    0x7034E4D6: "cScenarioArg",  # pc-only
    0x70405D37: "cNetEmc5",  # pc-only
    0x7044A39F: "MtCollada::Controller::MyDTI",
    0x7046C3DC: "rEffectSetData::POLYGON_FIX_TYPE",
    0x70482F1C: "CCalWavEncoder",
    0x704F4415: "rEffectSetData::ESD_SET_BILLBOARD",
    0x704FE852: "uToneMapFilter",
    0x7052EB0E: "uOm1307_Boat::cEventActBase",  # pc-only
    0x7055F27B: "cOmDoorActClose",  # pc-only
    0x705A77FC: "cEm22ActDie",  # pc-only
    0x705C44E7: "cEm20ActAtkInst",  # pc-only
    0x705D8122: "sVibration::VibControl",
    0x706375A1: "MC0_TIMING_CNTL_0",
    0x706444EB: "MtCollada::Texture::MyDTI",
    0x7064C959: "cEm42ActDeathBeatEscape",  # pc-only
    0x7069934A: "D1SCL_CRC_ENABLE",
    0x706B845B: "cPlAction_pl_act_coop_help_attack",  # pc-only
    0x706BA449: "AZ0_AZ2BC_CRC_READ",
    0x706CB8BB: "VGT_DRAW_INIT_FIFO_DEPTH",
    0x706D373B: "cFSMOrderCoopGate::FuncParamCoopGateSetActionClosed",  # pc-only
    0x706F1A3C: "cEmc0ActFinish",  # pc-only
    0x70728055: "cEm41ActShield",  # pc-only
    0x707628A4: "MtPhysicalAllocator::MyDTI",
    0x70767A28: "XAUDIO::CWaveFileWriter",
    0x70778901: "uLightScatteringFilter::MyDTI",
    0x7078A7B5: "_XUSER_PLAYERLIST_ITEM",
    0x707BD727: "sShader::ParameterDesc",
    0x707D53CA: "cEm0cActCatch",  # pc-only
    0x7080A9A7: "rEffectList::PARTICLE_OPTION_FLAG",
    0x70878AD1: "SCE_AH_LIST",  # pc-only
    0x7098BA40: "rSoundEngineValue::cValueData",  # pc-only
    0x7098BE9C: "CP_QUEUE_THRESHOLDS",
    0x709ACBB0: "FSB_LX_ERRINJ0",
    0x709D76C3: "ColorArray",
    0x709E4C4C: "MtCollada::Light::TYPE",
    0x70A3AEFE: "_DXVA_VideoPrimaries",
    0x70AB1E3F: "uOm092f::cActFire",  # pc-only
    0x70B2B07E: "rSoundDirectionalSet::DirectionalCurve",
    0x70B4B666: "uOm095b_Cliff::cActPlCliff",  # pc-only
    0x70BA1B6C: "VGT_OUTPUT_PATH_CNTL",
    0x70BE19A8: "tagVResultCode",
    0x70C2077E: "ID3DXLoadUserDataVtbl",
    0x70C33D30: "RPLL_CNTL_REG",
    0x70C375A4: "SCLK_SOFT_RESET",
    0x70C56D75: "MtGeomAABB::MyDTI",
    0x70C74CAC: "CCalPlayer",
    0x70CC7783: "uHazeFilter",
    0x70CE5B43: "EP_VENDOR_ID",
    0x70D1ADD8: "cPlAction_pl_act_attack_hook",  # pc-only
    0x70D924A5: "rEffectList::EFL_PARTICLE_CUSTOM",
    0x70E26C5F: "_D3DXPATCHINFO",
    0x70E47A38: "_ABCH_GET_CONTACTLIST_GAMERTAGS_RESPONSE",
    0x70E60D4B: "CGM_DRAM_CNTL_REG",
    0x70F3C148: "CSchemaAccess",
    0x70F528E2: "PCIEP_PORT_CNTL",
    0x70F690CD: "cAIFSM::StateFunc",  # pc-only
    0x70F98581: "sLightLinker::uCuboid",  # pc-only
    0x70FA4955: "cFSMOrder::FuncParamCheckEnemy",  # pc-only
    0x70FFEEB9: "_XMUHENDN3",
    0x7102B683: "sSoundN::VOICE_COMMAND",
    0x7103EA67: "HDC__",
    0x7104FA11: "cPlAction_pl_act_knife_ready_begin_from_weapon_ready",  # pc-only
    0x71053BE7: "XDVO_CRC_SIG_RGB",
    0x7105A46A: "XAUDIO::CMasterVoiceList",
    0x71060302: "uIdScope00",  # pc-only
    0x710ADCD2: "ID3DXAllocateHierarchy::__vftable",
    0x710AFEBB: "rShape::SHAPE_TARGET",
    0x710B01CA: "uScheduler::TRACK_WORK",
    0x710DD6CB: "_XMSG_SUMMARY",
    0x710F0454: "AZ1_LOOPBACK_PATTERN0PHS3",
    0x71134D41: "MtArray",
    0x711A7764: "sEffect::__vftable",
    0x711B99D9: "VGT_PERFCOUNTER0_HI",
    0x711ED62D: "tagLoopFilterColumnTable",
    0x7129FB44: "cEm10ActHighJump",  # pc-only
    0x712ACB2B: "CLIPPER_DEBUG_REG06",
    0x712C7AE2: "cEm84ActDmgGuard",  # pc-only
    0x71304BAA: "cTrans::Texture::MyDTI",
    0x71329731: "rShapeWeight::MyDTI",
    0x7135C778: "_DXVA_ConfigAlphaCombine",
    0x7138ABD0: "CLIPPER_DEBUG_REG15",
    0x71394359: "_XCONFIG_MEDIA_CENTER_SETTINGS",
    0x713ACA56: "NetworkRanking::ScoreOption",
    0x713D08A1: "PCIE_TX_CREDITS_CONSUMED_D",
    0x713F20AC: "cEm40ActNearCatchEscape_PL",  # pc-only
    0x7142F6A8: "cEm66Action",  # pc-only
    0x71469D10: "uOm0026::cActBreak",  # pc-only
    0x7147B818: "MtCollada::Imager",
    0x7147BA1D: "uDOFFilter::DOFPASS",
    0x7148B914: "cEm10ActAtkGunEmpWait",  # pc-only
    0x71490DF8: "ID00_DCP_DMIF_DATA_REQUEST",
    0x714AD3C8: "std::_Timevec",
    0x714BB657: "cEm61ActFreeFly",  # pc-only
    0x714D02AF: "cPositionFilterSectorFromPos",  # pc-only
    0x7151AFDA: "DC_LUTA_BLACK_OFFSET_RED",
    0x7151DBFB: "cEmA2ActGunDie_PL",  # pc-only
    0x7152FAEB: "_USER_PAYMENT_INFO",
    0x71534C1C: "sCollision::SbcInfoLowSet",
    0x7156669D: "uOm092f::cActPlBase",  # pc-only
    0x7157B34E: "_CQueueElement",
    0x715B0803: "MtDTI::__vftable",
    0x716014E2: "cEm80ActKataOk_PL",  # pc-only
    0x716331D3: "cPlAction_pl_act_wall_crouch_wait",  # pc-only
    0x7165347B: "BITRATESREC",
    0x716A51E0: "cOmEventPL_ActPre",  # pc-only
    0x716D87B2: "uAfterimage",  # pc-only
    0x716FFFE5: "NetworkConnectionStable::Window",
    0x71749789: "D1CRTC_BLANK_CONTROL",
    0x71762F59: "FSB_LX_IDLE_PATT",
    0x717905E3: "NetworkRankingLive::moveUpdateRanking::__l3",
    0x717C0C1D: "_XAMPLAYTIMERDATA",
    0x717CDA17: "cEm30ActRunStop",  # pc-only
    0x7182BBD8: "_D3DLIGHTTYPE",
    0x7188750D: "cEm44PlEvent_Escape",  # pc-only
    0x718E9ACB: "NetworkSessionManagerPat::P2pEvent",
    0x718EABBB: "XAUDIOFXINIT",
    0x71935A8E: "MSI_MAP",
    0x71950384: "rMovieOnDiskInterMediate",
    0x7199D6C0: "rEffectList::LIFE_TYPE",
    0x71A45770: "uOmJeep::cActPlActResult",  # pc-only
    0x71A47BFA: "cOmJeepAction_om_act_ev_00",  # pc-only
    0x71A7D4F7: "PIXMetaTilingData",
    0x71AB9731: "EP_BIST",
    0x71AC5E08: "PARSEREVENTINFO_NEWSTREAMDEC",
    0x71AF966F: "_DUMP_COLLECTION_FACILITY",
    0x71AFD976: "FSB_TX_DEBUG_HI_AND",
    0x71B29B05: "cEm6cActDie",  # pc-only
    0x71B94554: "FSB_TX_DEBUG_HI_OR",
    0x71B9BA3F: "XMEDIAPACKET",
    0x71BAC5E0: "PA_SC_PERFCOUNTER1_HI",
    0x71BB62B2: "rAIFSM::ParamProperty",  # pc-only
    0x71BDC38A: "cWpAction_wp_act_wesker_wait",  # pc-only
    0x71C1495C: "_IMAGE_RESOURCE_DIR_STRING_U",
    0x71C31F18: "rEffectSetData::COLL_FLAG",
    0x71C3D27E: "uOmLaserMirror::cActPlBase",  # pc-only
    0x71C6BE71: "_D3DSHADER_ADDRESSMODE_TYPE",
    0x71CEC497: "std::_Undefined_inner_type_tag",
    0x71D30D99: "cOmWindowAction_fence",  # pc-only
    0x71D8ACD9: "CP_RT8_COMMAND",
    0x71D95501: "XAUDIO::CStdFileStream::__vftable",
    0x71D9BAB5: "RB_HSIO_DLL_ADJ6",
    0x71DDC0F1: "sRender::TempTexture",
    0x71DE3802: "XAUDIO::SRC::DoubleVector",
    0x71DF34E0: "cEm32ActInvalid",  # pc-only
    0x71E413D6: "_D3DXIMAGE_INFO",
    0x71E43FE6: "_SYSTEM_AUDIT_OBJECT_ACE",
    0x71E746A7: "cOmCartridgeAction",  # pc-only
    0x71EC00BB: "XPLAYERLIST_RESULT",
    0x71EF3093: "cEm10ActAtkSpearHML",  # pc-only
    0x71F24E8E: "LOCALTALKER",
    0x71FED440: "sResource::__vftable",
    0x7200B9EC: "_REVOCATION_LIST_ENTRY",
    0x72047C09: "IDirectXFileObjectVtbl",
    0x720A1C6C: "CXStorageUploadWorker",
    0x720B62A5: "cEm30ActRunEnd",  # pc-only
    0x720C4080: "XECRYPT_ECPUB",
    0x72101699: "XAUDIO::CMutex::__vftable",
    0x7211EAC7: "cEm30ActSnarl2Wait",  # pc-only
    0x72175015: "cEm84ActCaught",  # pc-only
    0x7217B780: "_D3DPRIVATE_SCALER_PARAMETERS",
    0x7218397E: "cOmCoopDoorAction_om_act_wait",  # pc-only
    0x7218B8E2: "cEm20ActAtkHangingEscape",  # pc-only
    0x721AA243: "_FXLPIXELSHADERENTRY",
    0x721FB5D9: "tagSIZE",
    0x72256129: "XUIMessageInsDelItems",
    0x7225AB93: "PIX_INDEX_FRAME",
    0x7227296E: "TCB_CORE_DEBUG",
    0x722963E6: "PA_SC_DEBUG_QPP_1",
    0x722D4B4F: "HDESK__",
    0x7230A9A8: "FSB_TLA_COMPR_CARE_MASK1",
    0x72367BD9: "RTS_Z_DY_MSBS",
    0x7237EB26: "rEffectList::ENTRY_TYPE",
    0x723F7918: "uOmCoopJumpBroad::cActWaitJumpReady",  # pc-only
    0x7241E3B4: "_FILE_NAME_INFORMATION",
    0x724ACC4C: "XECRYPT_RSAPUB_1024",
    0x724EF301: "TP0_CHECKSUM_PIXEL_2",
    0x724F716C: "sRender::__vftable",
    0x725238E3: "NetworkCommunity",
    0x7253C563: "SQ_WRAPPING_1",
    0x7253F9B3: "_D3DXSHADER_FILEINFO",
    0x72560BE9: "sSoundN::SpeakerAngle",
    0x72573694: "cPlAction_pl_act_weapon_change",  # pc-only
    0x7259EAD5: "_D3DCOLORVALUE",
    0x725E42BA: "uEffectVFR::LifeKeyframe",
    0x726B84C0: "uEffectVFR::Adhesion",
    0x726BCB74: "_HAL_GPIO_ACTION",
    0x7273DEF0: "TP0_PERFCOUNTER1_HI",
    0x7282D4B1: "_D3DTRANSFORMSTATETYPE",
    0x72836F33: "tagWMCIndexSpecifier",
    0x72842A2A: "sPad::KIND",
    0x7286688A: "MtCollisionTree::Node",
    0x728FDC54: "IXuiDevice",
    0x72900674: "D3D::CPerfCounters",
    0x7298F2DD: "uOmSwitch3::cActPush2Mid",  # pc-only
    0x72991E73: "sCollision::SbcInfo",
    0x729CCFE6: "_P_BLOCK_MSG",
    0x729D2275: "MtCollada::Param",
    0x729FA97F: "D3D::CMicrocodeBuilder::Microcode",
    0x729FB5E8: "sSoundN::REQUEST_TYPE",
    0x72A1B0E5: "cPlAction_pl_act_damage_fire",  # pc-only
    0x72A2F5BF: "_RAM_TABLE",
    0x72A8BF28: "DepthformatX",
    0x72BBA8EF: "sParameter::PARTS_DISP_PARAM_STRUCT",  # pc-only
    0x72BDA632: "cNetEm44",  # pc-only
    0x72BECF9A: "uOm0944::cActLiftDown",  # pc-only
    0x72C0B725: "PIX_DECODE_VIDEO_DATA",
    0x72C2DCF7: "PCIE_PERF_COUNT_CNTL",
    0x72C53F0D: "_PredictMVLUTPullBack",
    0x72C9CBF5: "_SVOD_LEVEL1_HASH_BLOCK",
    0x72CB951D: "_WAKEUP_MANAGER_INTERVAL",
    0x72D3EFD8: "PostProcDrcDataFormat",
    0x72D83EA9: "PIX_REQUEST_CPU_TRACE",
    0x72D879D9: "PCIE_ERR_SRC_ID",
    0x72D96099: "_D3DXMATRIXA16",
    0x72DB8BDF: "XUIMessageLineCount",
    0x72DCB243: "cEm40ActNearEscape",  # pc-only
    0x72DE6C40: "_SYSTEM_AUDIT_ACE",
    0x72E43A26: "rEffectList::EFL_KEYFRAME_U32",
    0x72E4E32A: "_HVPOWER_MODE",
    0x72E564AA: "GPUINDEXSELECT",
    0x72E792A3: "cPlAction_pl_act_damage_blow_s",  # pc-only
    0x72EBFE35: "_SVOD_DEVICE_DESCRIPTOR",
    0x72EF304D: "MtCollada::Asset::UP_AXIS",
    0x72F0688D: "LLMDecodeCoefStatus",
    0x72F100CB: "uOmS705ceil::cEvActStopEm",  # pc-only
    0x72F1AF9E: "_ACE_HEADER",
    0x72F62654: "cAIModule",  # pc-only
    0x72FB0A01: "uOma00b_LaserArea::Pos",  # pc-only
    0x72FDE2D8: "MtPreProcessor::INBUF",
    0x72FE4C33: "ScrHideList",  # pc-only
    0x7300D462: "_STF_HASH_BLOCK",
    0x73035C2A: "_D3DXSHADER_COMPILE_PARAMETERSA",
    0x730643BD: "UVBASE_REQUESTVOICECHATPARAM",
    0x7308731D: "cFSMOrderEm42::FuncParamSetAction_Em42",  # pc-only
    0x730C8111: "_XONLINE_QUERY_ATTRIBUTE_BLOB",
    0x7310C3C8: "CCalWavEncoder::WaveFormatChunk",
    0x7311360A: "_XENUMERATEPARAM",
    0x731224CC: "TP1_CHECKSUM_PIXEL_0",
    0x73152214: "PCIE_CONFIG_CNTL",
    0x731597AD: "TP3_PERFCOUNTER1_LOW",
    0x731D793B: "rEffectList::EFL_PARTICLE_RADIAL_BLUR_FILTER",
    0x731E7CA5: "cFSMOrder::FuncParamUnitOnOff",  # pc-only
    0x7322835E: "_EXCEPTION_RECORD64",
    0x73254D4E: "EP_ADAPTER_ID_W",
    0x7325DE3B: "_SID",
    0x7334C33F: "_D3DDEVICE_CREATION_PARAMETERS",
    0x73359EAE: "_UNICODE_STRING",
    0x73363384: "AZ0_MRT_STATE_DWORD1",
    0x73363B4C: "sShader::FUNC_SHADOW_BLOCKER",
    0x73377D4A: "GPU_TESSELLATORPACKET",
    0x733A490E: "CP_DMA_DST_ADDR_STAT",
    0x733D9282: "cFSMOrderDoor::FuncParamDoorCheck",  # pc-only
    0x733FD046: "BRTLBTICKET",
    0x73466B26: "_FILE_OBJECT",
    0x734A460B: "uLt00",  # pc-only
    0x734D7173: "cTrans::VolumeTexture",
    0x734E384B: "cTrans::ExternalRegion",  # pc-only
    0x73543690: "_XCHALRESP_STATS",
    0x7357F5B3: "cEm84Action",  # pc-only
    0x735CF2D9: "cFSMOrder::FuncParamUnitKill",  # pc-only
    0x735F118C: "AZ1_EDRAM_INIT",
    0x735F8E76: "cOmDoorActOpenEM",  # pc-only
    0x735F9BAF: "cFSMOrder::FuncParamFade",  # pc-only
    0x7363236B: "ID15_BLEND_DATA_B",
    0x7364EE70: "PA_SU_LINE_CNTL",
    0x73664E10: "cEm22ActWalk",  # pc-only
    0x736A1581: "MtCollada::Optics",
    0x73704205: "MPARAM_POLAR3",
    0x7375697C: "rEffect2D::E2D_KEYFRAME_VECTOR",
    0x7375BF3A: "AZ0_LOOPBACK_PATTERN0PHS0",
    0x737C44E5: "XUIMessageSmoothScroll",
    0x737CBA3A: "MT_ENUM",
    0x7380938E: "XAUDIOFXDATAPARAM",
    0x7383DD19: "IDirectXFileBinary::__vftable",
    0x73850D05: "rArchive",
    0x738B7EA2: "XUINotifyValueChanged",
    0x738D3204: "CP_RT3_COMMAND",
    0x73920949: "_D3DFORMAT",
    0x7393655F: "CXuiHtmlControl",
    0x7397CF0A: "sGpuParticle::FUNC_PRIM_BASEMAP",
    0x739C6284: "cEm43ActDownEnd",  # pc-only
    0x739F0345: "std::domain_error",
    0x739FE873: "_XUID_AND_FLAGS",
    0x73A06E25: "MtCollada::Translate::MyDTI",
    0x73A2D987: "DecRunLevelVecState",
    0x73A77168: "XAUDIOVOICEFXCHAIN",
    0x73A8D103: "cEma2ActHumituke_Esc_PL",  # pc-only
    0x73AA4A12: "Instruction_serial",
    0x73AE07D5: "CCalAudioDecoder",
    0x73BB79B4: "cPlAction_pl_act_die_common",  # pc-only
    0x73BC4DFE: "cFSMOrder::FuncParamPlayerCheck",  # pc-only
    0x73C03880: "uToneMapFilter::RTCLEAR",
    0x73C83F24: "SQ_CF_RT_LOOP",
    0x73CA427C: "D3D::CValidate",
    0x73CDB059: "PCIE_PERF_COUNT1_SLV_S_C_CLK",
    0x73CFBF15: "cEm10ActAtkGunBombPeepL",  # pc-only
    0x73D128A3: "cEm40ActNearCatch",  # pc-only
    0x73D4F8CD: "CXContentDownloadMedia::REFERRAL_RESPONSE_BUFFER",
    0x73D83BC7: "DCPERFEVENT",
    0x73DBC53C: "MC0_PERFCOUNTER0_CNTL",
    0x73DDC1ED: "cEm6fActDmgAir",  # pc-only
    0x73DE50CA: "MtCollada::Node::MyDTI",
    0x73E2CEAF: "rEffectStrip::EFS_HEADER",
    0x73E2E8C1: "uOm092e_LaserBlock::cActPlKick",  # pc-only
    0x73E4F84E: "IXAudioVoice",
    0x73E893AD: "cEm43ActHookBSecond",  # pc-only
    0x73E9367F: "cPlAction_pl_act_die_fall_cliff",  # pc-only
    0x73EA6FA2: "_WMAEncAdvancedFormatOpts",
    0x73EB1731: "CXuiProgressBar",
    0x73EB1796: "_FXLVERTEXSHADERENTRY",
    0x73EFA28B: "GpuMocomp",
    0x73F48F0F: "DMSTATE",
    0x73F8638F: "D1GRPH_SECONDARY_SURFACE_ADDRESS",
    0x73FCD1A4: "XCOMPRESS::_StreamEncoderBlockInfo",
    0x73FEF7D5: "NetworkLayer::Member",
    0x740501A1: "rEffect2D::RANGE_OPTION_FLAG",
    0x74071B08: "_FP_32",
    0x74075491: "RBBM_PERFCOUNTER2_LO",
    0x74075D65: "STATUS",
    0x7409C149: "_VESA_STANDARD_TIMING",
    0x740D6A59: "cEm84ActFallOffHandrail",  # pc-only
    0x74107906: "cEm62ActDie",  # pc-only
    0x7410E623: "_COPP_ConnectorType",
    0x741B92D9: "uJointAnimator::JOINT_BUFF",
    0x741E8F7F: "uEm45::cActPlBase",  # pc-only
    0x74221BC8: "sArea::AreaInfo",
    0x7422391F: "_BASIC_GENRE_INFO",
    0x742647DE: "D3D::CDevice",
    0x742737A9: "CCalRcvDecoder",
    0x742775DD: "NetworkMultipleUdpLive::__vftable",
    0x7427BDB8: "_GET_FILEEX_INFO_LEVELS",
    0x742AEE00: "IOCPERFREGISTER",
    0x74326C01: "RBBM_STATUS2",
    0x7432DC56: "rArchive::RESOURCE_INFO",
    0x7432ECD3: "SQ_PERFCOUNTER2_HI",
    0x7434E2D0: "cItAction_it_act_get",  # pc-only
    0x743EB114: "PA_SC_AA_MASK",
    0x744112F0: "uOmS705ceil::cActBroken",  # pc-only
    0x744220C7: "cPlAction_pl_act_item_dump_second",  # pc-only
    0x7445F0AB: "rEffectSetData::ESD_PARAM_CULLING",
    0x7448468B: "cItAction_it_act_drop",  # pc-only
    0x74489E13: "XONLINE_GENRE_TYPE",
    0x7449C72D: "SQ_CF_PROGRAM_SIZE",
    0x744A826B: "sEffectVFR::MyDTI",
    0x744F449B: "DC_LUTA_WHITE_OFFSET_RED",
    0x744FAB23: "CCalWavEncoder::WaveChunkHeader",
    0x7451D2FB: "uLight::__vftable",
    0x745670E9: "D3D::CCapture::HashMap",
    0x745704B6: "uOmSwitch::cActSwitchOff",  # pc-only
    0x7459E459: "MtCollada::Technique",
    0x745AC30E: "PA_SC_AA_CONFIG",
    0x745B1933: "rEffectSetData::ESD_SET_HIT",
    0x745B2100: "uOm090d_Floor::cActWait",  # pc-only
    0x745C9705: "GpuIntra",
    0x746BB7FA: "RB_HSIO_OE_OVERRIDE",
    0x746BDCBF: "NB_REVISION_ID",
    0x746DD3F3: "AHShapePolygon::PolyIndex",  # pc-only
    0x747566B8: "METADATAENTRY",
    0x747C9385: "sShader::FUNC_SHADOW_ALBEDO_ALPHA",
    0x747CDCBA: "rMotionList::MOTION_LIST_HDR",
    0x747D9C27: "_ACCOUNT_TROUBLESHOOT_RESPONSE",
    0x7481D792: "NetworkLayer::DeliveryReceive",
    0x74821923: "_TIMER_BASIC_INFORMATION",
    0x7487F134: "MtFCurve::DescKey",
    0x748F26AC: "_XPROFILE_RACE_BRAKE_CONTROL_OPTIONS",
    0x74918892: "PCIE_PERF_COUNT1_MST_R_CLK",
    0x74932388: "_D3DRECTPATCH_INFO",
    0x7494F854: "rHavokConstraintLayout",  # pc-only
    0x749838DE: "cPlAction_pl_act_attack_neck",  # pc-only
    0x74984654: "STREAMDATAINFO",
    0x749AEB52: "IProcMode",
    0x74A151AE: "_D3DXPRIORITY_TYPE",
    0x74A187E8: "CARDEA_CSP_INTERFACE",
    0x74B0BC02: "_FSCACHE_ELEMENT",
    0x74B42348: "_PROFILEENUMRESULT",
    0x74B6A30C: "PatInterface::FoBinaryNtc",
    0x74B6FC69: "uEffectVFR::PTCL_FLAG",
    0x74B99E12: "FSB_LX_DEBUG_LO_OR",
    0x74BB54C6: "_HEAP_VIRTUAL_ALLOC_ENTRY",
    0x74BC98F5: "BIOS_8_SCRATCH",
    0x74BEF74D: "cEm8cAtkJavelinThrow",  # pc-only
    0x74BFAC59: "sObjModel::ReflectionManager",  # pc-only
    0x74C5F059: "rEffectList::EFL_MOVE_PATH_CHAIN",
    0x74CE0DDA: "_Q_MESSAGE_SUMMARY_2",
    0x74D082EE: "_IMAGE_RELOCATION",
    0x74D43E5A: "DC_GPIO_XDVODATA_A",
    0x74D7E6A0: "aS103::cActUroBurnt",  # pc-only
    0x74DB43AE: "PCIE_P_IMP_CNTL_UPDATE",
    0x74DC6B75: "_XEX_HEADER_STRING",
    0x74DE47AF: "XAUDIO::CRouterEffect::__vftable",
    0x74DFB8D7: "cEm63ActDash",  # pc-only
    0x74E05608: "cEmc2ActMove",  # pc-only
    0x74E41F1D: "MtCollada::Animation::MyDTI",
    0x74E6098F: "BIU_PERFCOUNTER2_LOW",
    0x74E7D1BB: "cPlAction_pl_act_item_put_first",  # pc-only
    0x74EC3D0F: "MtObject::__vftable",
    0x74F15F28: "MtHeapAllocator",
    0x74F1FC01: "aConvertBase",  # pc-only
    0x74F50845: "CP_ME_VS_EVENT_ADDR_SWM",
    0x74FFD794: "uCapsuleCubeMapLight::MyDTI",
    0x7502FB1C: "CHuffmanBitObj",
    0x7503069C: "rEffectSetData::ESD_SET_CULL_POLYGON",
    0x750315E2: "_P_QUERY_AFFILIATES_MSG",
    0x7504B070: "cPlAction_pl_act_ext_wait",  # pc-only
    0x7507104C: "SCRATCH_CMP_LO",
    0x750A54DB: "_FILE_DISPOSITION_INFO",
    0x751163FB: "GLAREDEF",
    0x75131DE8: "TCD_INPUT1_DEBUG",
    0x75167EAA: "MtFloat4",
    0x7518FF82: "cEm22ActAtkCritical",  # pc-only
    0x751C49F6: "uOm08b6_S309Elev::cActRise",  # pc-only
    0x7521B1F7: "tagWMCIndexInfo",
    0x7525312B: "PatInterface::MailBody",
    0x752ABECF: "uModel2Light",
    0x752E18B2: "MtCollada::Light::MyDTI",
    0x752E8A62: "cEm32ActCornerUp",  # pc-only
    0x75307CAB: "AHEffectData",  # pc-only
    0x7534E4DB: "uCubeMapLight::MyDTI",
    0x7537DE0E: "NetworkPeerMultipleUdp",
    0x75389616: "rSoundPackageXml::SplitData::MyDTI",
    0x7538DF2E: "cEm83ActDmgNormalU",  # pc-only
    0x753D04B7: "_DXVA_COPPSignature",
    0x75400A88: "ISequentialStream::__vftable",
    0x75416C40: "_CONTENT_AVAILABLE_REQUEST",
    0x7546C652: "cOmChainAction_wait",  # pc-only
    0x754B82B4: "rAreaHitShape",  # pc-only
    0x754E28CA: "cNetEnemy",  # pc-only
    0x754F883F: "MP4SampleSizeAtom",
    0x755409B0: "uOmCrank::cActWind",  # pc-only
    0x75593F78: "MtXmlReader::Handler",
    0x755F0030: "__RAW_READ_INFO",
    0x756307BA: "cEm10ActDmgFlash",  # pc-only
    0x75636BBC: "MtCollada::Vertices",
    0x7568BE93: "cEm84ActFire",  # pc-only
    0x756C55AC: "FB_START",
    0x7570C1C7: "SQ_CONSTANT_VFETCH_1",
    0x7571347F: "_XOVERLAPPED",
    0x75734983: "VENDOR_ID",
    0x757538ED: "NB_LATENCY",
    0x75767777: "DC_TEST_DEBUG_TRIGGER_STAT",
    0x757E88D9: "uOm021c_Switch::cActBase",  # pc-only
    0x7580538B: "MC0_TUNING_0",
    0x7580F6F4: "XG_MCT::_MCTDECOMPRESSION_CONTEXT_HEADER",
    0x75870AA2: "IStream",
    0x758B2EB7: "rCommonEffect",  # pc-only
    0x758B6B32: "_OFFER_PURCHASE_REQUEST",
    0x758FC226: "uEffectVFR::Chain",
    0x75947CAC: "COverlapAddData",
    0x75966495: "DC_TEST_DEBUG_OUT_TEST_DATA",
    0x75970527: "XAUDIO::CHeapMemoryManager",
    0x7598E453: "uOmSwitch3::cActPull2Mid",  # pc-only
    0x75993F81: "cEm84ActCatch",  # pc-only
    0x759CA8AE: "TCB_TAG0_DEBUG",
    0x759D1192: "cDemoLoopMovie",  # pc-only
    0x759E50D6: "AacDriverPerformance",
    0x75A0AD2A: "HIT_PARAM",  # pc-only
    0x75A25040: "RB_PERFCOUNTER0_HI",
    0x75A55E8D: "RB_BLEND_ALPHA",
    0x75A780A6: "cEm82AtkDrillEscape_PL",  # pc-only
    0x75B2F2A5: "GPUALLOCBUFFERSELECT",
    0x75B6869D: "rEffect2D::PARTICLE_OPTION_FLAG",
    0x75B6FF00: "_I3DL2_LISTENERPROPERTIES",
    0x75BDA853: "_FILE_ATTRIBUTE_TAG_INFORMATION",
    0x75BEA5F2: "MDLL_CNTL1_REG",
    0x75BF4B75: "cEm10ActDmgGuard",  # pc-only
    0x75C29E10: "GPUFLOWOP",
    0x75C86534: "PA_SU_POINT_SIZE",
    0x75C928A9: "IXoCallback",
    0x75CA154E: "rAIFSM::Condition",  # pc-only
    0x75CB061B: "_DXVA_IBlkPosInP",
    0x75D0622B: "cNetEm40",  # pc-only
    0x75D42F75: "XAUDIO::CCriticalSection",
    0x75D515B3: "TP1_PERFCOUNTER1_HI",
    0x75D52A42: "_XMSG_GET_PROP_REQUEST",
    0x75D626F1: "TCF_PERFCOUNTER1_HI",
    0x75D7EBD7: "MtColorHLS",
    0x75DE0F6F: "_XENUMERATOR_STATS",
    0x75DF89C6: "RB_BLEND_GREEN",
    0x75DF944E: "cPlAction_pl_act_wall_stick_turn_l",  # pc-only
    0x75E02498: "_XONLINE_LOGON_PARAMS",
    0x75E6E758: "_XONLINE_SERVICE_INFO",
    0x75EFEFFF: "RB_DEBUG_1",
    0x75F1BBF3: "cEm32ActAtkUpper",  # pc-only
    0x75F7CFD0: "D1GRPH_COLOR_MATRIX_COEF_1_1",
    0x75F87FC8: "sVibration::CameraVibration::__vftable",
    0x7601F852: "MP4TrackReferenceAtom",
    0x760294FF: "_PM4CMDWAITFORIDLE",
    0x7602CC49: "PerChannelInfoENC",
    0x7604849E: "XAUDIO::CAutoFloatingPointState",
    0x76071A0D: "uEffectEdit::PARTICLE_DRAW_PARAM",
    0x760D949F: "cOmDoorEventPL_ActOpenKick",  # pc-only
    0x760E73DD: "SBR_ELEMENT_STREAM",
    0x7611E454: "PA_SC_DEBUG_Z_0",
    0x7614E31E: "cMaterialStandard::PIPELINE_STANDARD",
    0x761980AC: "fd_set",
    0x761B299A: "_CDiffMV",
    0x761C61BE: "uEffect2D::Generator",
    0x761C886F: "NetworkXboxVoice::EffectParam",
    0x7620A2E7: "RENDERERBUFFER",
    0x76250B37: "cEm10ActAtkGunShotRR",  # pc-only
    0x762800D4: "uOm1316_BackupHeli::cActAttack",  # pc-only
    0x7629A017: "cAIPositionEvaluationObject",  # pc-only
    0x762A155D: "ISOMatrixRecord",
    0x762DEB07: "rClothXml::Constraint::MyDTI",
    0x762EF7A7: "GPUPERFEVENT_SQ",
    0x763254CA: "MtSerializer",
    0x76333C19: "D1SCL_MANUAL_REPLICATE_CONTROL",
    0x76341666: "uOm0927_Crane::cActQuitInit",  # pc-only
    0x763735DD: "uOmKickSwitch::cActPlBase",  # pc-only
    0x763F1EB9: "_DXVA_Deblock_H264",
    0x7641660F: "MtCollada::Instance",
    0x76451DF2: "cFSMOrderPlayer::FuncParamVoice",  # pc-only
    0x7645C6F8: "_D3DBLENDSTATE",
    0x7646A581: "rEffectList::POLYGON_FIX_TYPE",
    0x7646E594: "cTrans::CMD_DRAW",
    0x76470F32: "CLIPPER_DEBUG_REG02",
    0x7649B2BF: "uOmKickSwitch::cActReturn",  # pc-only
    0x764BE34A: "cPlAction_pl_act_attack_combo_finish",  # pc-only
    0x764BFEC5: "_XE_CONSOLE_CERTIFICATE",
    0x764C9F3B: "cOmLadderAction_stand",  # pc-only
    0x764FE24B: "XUIMessageHittest",
    0x7651EC95: "cEm43ActGrenadDamageStart",  # pc-only
    0x76524248: "FILEOUT_EXTENSION",
    0x76556FC9: "CLIPPER_DEBUG_REG11",
    0x7657CD4F: "uSingleLSM",
    0x76598653: "MtGeometry::__vftable",
    0x7662AF2C: "PIX_XBDM_COUNTERS",
    0x7662E147: "uEffectVFR::LINE_FIX_WORK",
    0x7669A745: "FSB_LX_PMC0_AND",
    0x766DA04E: "XAUDIOROUTERFXINIT",
    0x766F8E1D: "cEm30ActDmgFire",  # pc-only
    0x76731BBE: "D1GRPH_COLOR_MATRIX_COEF_3_1",
    0x76820D81: "rMotionList",
    0x76827C87: "SDSTATE",
    0x76834EE0: "rEffectList::EFL_PARAM_CLOTH_CHAIN",
    0x7688046A: "VC_PERFCOUNTER2_SELECT",
    0x768ED08A: "sShader",
    0x768F835D: "VQ2_MBlk",
    0x769318B0: "CP_RT9_SIZE",
    0x76993C2C: "GpuFilterInfo",
    0x769A514C: "CP_RT14_REFERENCE",
    0x769BCC1B: "cEmc2ActDrag",  # pc-only
    0x76A363BD: "XECRYPT_MD5_STATE",
    0x76A94EB1: "_P_PRESENCE_ENUM_CREATE_MSG",
    0x76A9F0C5: "cEm43ActBackPunch",  # pc-only
    0x76AC53D9: "MP4EditListAtom",
    0x76B05C91: "GPUCmdMocomp",
    0x76B45A05: "_COPP_StatusHDCPFlags",
    0x76B47EAC: "RB_HSIO_DLL_ADJ2",
    0x76B86F55: "uShadowLight::TYPE",
    0x76BC8288: "CXContentDownload",
    0x76BE09BF: "stdext::bad_alloc",
    0x76C0CF5B: "cEm41Action",  # pc-only
    0x76C1FC2E: "TP1_PERFCOUNTER1_LOW",
    0x76C2A6AB: "cEm45ActDamage",  # pc-only
    0x76C33947: "_WAKEUP_MANAGER_ALARM_ID",
    0x76C64F4F: "TP3_CHECKSUM_PIXEL_0",
    0x76C77294: "_XUSER_PROFILE_SETTING",
    0x76C7F545: "CCalBase::POSITION",
    0x76CA13D7: "uSpotShadowLight",
    0x76CABE43: "SC_PERFCNT_SELECT",
    0x76CB3172: "uIdTitle02",  # pc-only
    0x76D25A07: "SQ_INSTRUCTION_CF_ALLOC_0",
    0x76D2EF9F: "sCollision::Collider",
    0x76E059C7: "CP_RT15_MASK",
    0x76E0F8DD: "cEm8eAtkTornado",  # pc-only
    0x76E5191B: "MtStream",
    0x76E79D8B: "_CRT_FLOAT",
    0x76E814C2: "rEffectList::COLOR_FLAG",
    0x76E90628: "BIOS_3_SCRATCH",
    0x76EBDC4C: "MPPACKET",
    0x76F517B0: "cEm8eAction",  # pc-only
    0x76F628AD: "_POSTAL_CODE_MATCH",
    0x76F7916E: "rEffectList::EFL_MOVE_NONE",
    0x76F87D0F: "TCR_PERFCOUNTER0_LOW",
    0x76F883BC: "rSoundRequest::SOUND_REQUEST_CATEGORY",
    0x770B6CD2: "_XNET_LOGON_NAT_TYPE",
    0x770D0C2C: "_D3DFILLMODE",
    0x77147CD2: "VOPpredType",
    0x77165D98: "cEm32ActDmgStruggle",  # pc-only
    0x771673EA: "cFSMOrder::FuncParamFreeS",  # pc-only
    0x77168421: "ID3DXMeshVtbl",
    0x77170222: "_P_DELETE_MSG",
    0x771713D4: "_XSHOWFEEDBACKUI_PARAMS",
    0x77178FFA: "MH_PERFMON_PERFCOUNTER0_SELECT",
    0x77187CED: "_STRING_DATA",
    0x77188ED9: "rRenderTargetTexture::MyDTI",
    0x771ADCAA: "cAtkParam::HitUnit",  # pc-only
    0x7725F64F: "rSoundCurveXml::Curve::MyDTI",
    0x772790A2: "_XUSER_MUTELIST_REQUEST",
    0x772FA349: "_XMFLOAT2",
    0x7731D1A8: "std::allocator",
    0x773974F0: "D3D::OutputInterpolatorUseContext",
    0x77418F7C: "sShader::ENVELOPE_HANDLE",
    0x77453C1E: "PA_SU_PERFCOUNTER2_SELECT",
    0x77472463: "cEm84ActStripped",  # pc-only
    0x774F70C6: "cAIFSMFuncParam",  # pc-only
    0x775454C6: "cOmTestAction",  # pc-only
    0x7754DD26: "cTrans::TextureBase::LOCKRECT",
    0x775FE982: "GPU_POINTPACKET",
    0x77615CE0: "CXStorageDownloadToMemory",
    0x77651920: "ID3DXMesh::__vftable",
    0x77659BA8: "MtCollada::Texture",
    0x776613A1: "CP_DEFAULT_SC_BOTTOM_RIGHT",
    0x776AF359: "_XMUDECN4",
    0x776BB04B: "MtCollada::Array",
    0x776F73DE: "rModel::BOUNDARY_INFO",
    0x77724DD3: "CCalImageInfo",
    0x77745893: "SCRATCH_REG5",
    0x7776E84C: "AHShapePolygon",  # pc-only
    0x777C377E: "cEm10ActDmgSulfate",  # pc-only
    0x777E890F: "GPUDEPTHARRAY",
    0x7782376A: "CP_ME_RT_DATA",
    0x7782721D: "LATENCY",
    0x779A9882: "TP2_CHECKSUM_PIXEL_2",
    0x77A0D700: "ID08_LUT_CONTROL",
    0x77ACD113: "rShape::SHAPE_HDR",
    0x77AE10FB: "uOmLaserMirror::cActPlReady",  # pc-only
    0x77AE6BA8: "uEffectVFR::STATUS",
    0x77B0194F: "GPUHIZFUNC",
    0x77B17189: "D1GRPH_COLOR_MATRIX_COEF_2_1",
    0x77B82EF0: "IOC_PERFCOUNTER0_SELECT",
    0x77BBDB6E: "rSoundRequestXml::ElementData",
    0x77C545ED: "_DUMP_STANDARD_BUCKET_DATA",
    0x77C68247: "NB_VENDOR_ID",
    0x77C88D1E: "cFSMOrder::FuncParamRandomEnemy",  # pc-only
    0x77CB32A9: "PA_SC_DEBUG_SPARE",
    0x77D0381C: "tagRGBQUAD",
    0x77D61389: "RB_PERFCOUNTER0_SELECT",
    0x77D6C9DD: "uHSVFilter::MyDTI",
    0x77D9225A: "tagWMVAsyncProp",
    0x77DF805C: "XUIMessageChildAdded",
    0x77DF8ECD: "MP4UnknownAtom",
    0x77E3C462: "std::ios_base::event",
    0x77E3F092: "cFSMOrderCharacter::FuncParamKeepArea",  # pc-only
    0x77E7B756: "uFacial",
    0x77E93FF1: "_D3DXATTRIBUTERANGE",
    0x77EA0363: "uLevelCorrectFilter::MyDTI",
    0x77ECBD55: "MtCollada::Source::MyDTI",
    0x77F7AE12: "MPARAM_POLAR3KEY",
    0x77FE6DAD: "XG_MCT::CXCodec",
    0x78011B70: "_DM_HID_KEYBOARD_DATA",
    0x780554A9: "cObjAdjTree::Node::AdjUnit",  # pc-only
    0x78070389: "VC_PERFCOUNTER1_SELECT",
    0x7808707D: "SCRATCH_CMP_HI",
    0x7808757B: "HBITMAP__",
    0x7808EA10: "rRenderTargetTexture",
    0x7810AC1E: "CONFIG_XSTRAP3",
    0x78121520: "OLDINDEXINFO",
    0x7817EB09: "uOm0927_Crane::cActWait6",  # pc-only
    0x781A5C3A: "_BY_HANDLE_FILE_INFORMATION",
    0x781CB619: "_BASIC_SUBSCRIPTION_INFO",
    0x781E2D33: "tagMoreUserData",
    0x782795E3: "PIX_STREAM_STATUS",
    0x7827D583: "cAIFlockManager",  # pc-only
    0x7837C3BA: "cOmBoatAirAction_pl_act_damage_cockpit",  # pc-only
    0x783AE277: "_XGCPUSHADERVERTEXSTREAM",
    0x783DCB90: "uPLCamera",  # pc-only
    0x78409258: "ID3DXFileEnumObjectVtbl",
    0x78443D05: "sMain::MyDTI",
    0x78448E7E: "uOm08e3_RuinTrap::cActPlFailed",  # pc-only
    0x78452F08: "D3D::MajorMode1InputRegs",
    0x784AAF19: "cPosHokanParent",  # pc-only
    0x784F761A: "uEffectVFR::Polyline",
    0x784FC8B8: "cEm71Action",  # pc-only
    0x78528108: "BRTKEEPALIVESTATE",
    0x7852E0F1: "cEm62ActEscape",  # pc-only
    0x785A06EC: "uModelSky::MyDTI",
    0x785BD903: "uNoiseFogFilter",
    0x78649FEF: "PA_SU_VTX_CNTL",
    0x786BA193: "VdpHeader",
    0x786C39DC: "_SYSTEMTIME",
    0x786CBB49: "MtFloat3A",
    0x786EB845: "_XPROFILE_PREFERRED_COLOR_OPTIONS",
    0x7873002D: "XGUCODESHADERVERSION",
    0x78758BC9: "_XPROFILE_RACE_ACCELERATOR_CONTROL_OPTIONS",
    0x7878F21C: "cEm6dActDamage",  # pc-only
    0x78794EBA: "CP_RT7_REFERENCE",
    0x787A411C: "ID3DXAnimationSet::__vftable",
    0x787A7C88: "rFacialPattern::MyDTI",
    0x787AD3E4: "cEm10ActNeckHangEscape_PL",  # pc-only
    0x787D5EBD: "_ACCESS_ALLOWED_OBJECT_ACE",
    0x78867D49: "cWpAction_wp30_act_light_get",  # pc-only
    0x788A93A2: "uOm090c_BeltShutter::cActWait",  # pc-only
    0x788F3688: "_XCHALRESP_STATS_NODE",
    0x78906A5D: "rSoundRandomXml::MyDTI",
    0x7892ABE1: "CXuiRadioGroup",
    0x789712C9: "cFSMOrder::FuncParamPlayerPoint",  # pc-only
    0x7898CAD5: "uOma005_Stairs::cActEvWait",  # pc-only
    0x78A6663D: "cEm65ActAttack",  # pc-only
    0x78ABF16A: "cEm8cAtkDrillRelease",  # pc-only
    0x78AF5BD9: "PA_SC_DEBUG_ITER_3",
    0x78B11D34: "ARG_TYPE",
    0x78B18C18: "cEm10ActWait",  # pc-only
    0x78B972AD: "GpuLoopFilterV9",
    0x78C00117: "cOmCoinActDie",  # pc-only
    0x78C8B2F2: "uOmS109_Driver::cActBase",  # pc-only
    0x78C96CE0: "cEm0bActWait",  # pc-only
    0x78CE8A63: "_HEAP_STOP_ON_VALUES",
    0x78D243D6: "MtCollada::Asset::MyDTI",
    0x78DCF112: "uEnvMap::MSAA",
    0x78DE190D: "rModel::MODEL_HDR",
    0x78E0558E: "TCM_PERFCOUNTER0_HI",
    0x78E072AA: "GPUPERFEVENT_VC",
    0x78E8D875: "rCameraListXml",
    0x78ED7D7F: "_XGAMERPROFILE_PARAMS",
    0x78EDFF60: "cOmCartridgeAction_om_act_throw",  # pc-only
    0x78EEF867: "SB_INTBAR",
    0x78FB4EBD: "_STFC_BLOCK_CACHE_ELEMENT",
    0x79030232: "cFSMOrder::FuncParamEtcItem",  # pc-only
    0x79049816: "rEffectList::CLOTH_CURVE_TYPE",
    0x7906F7B0: "sMain::JOB_THREAD",
    0x7907A634: "_D3DTEXTUREOP",
    0x790834A0: "RBBM_PERFCOUNTER2_HI",
    0x79119942: "cLinkUnit::cTargetBase",  # pc-only
    0x7915D0AD: "_D3DCMPFUNC",
    0x791838CC: "_XONLINE_QUERY_ATTRIBUTE_STRING",
    0x791B328F: "SQ_FETCH_4",
    0x791E4589: "SCL1_HFILT_IO",
    0x791EFCD5: "CP_MIU_TAG_STAT0",
    0x79225043: "cItem",  # pc-only
    0x7926010F: "cEm32ActAtkScratch",  # pc-only
    0x79280C08: "CP_DMA_TABLE_ADDR",
    0x792AF2CD: "cFSMOrder::FuncParamEvent",  # pc-only
    0x792B46C0: "uLight",
    0x79372913: "IOC_PERFCOUNTER3_SELECT",
    0x793C3C25: "CCalGraphicsRenderer::__vftable",
    0x793F8C16: "_FIBER",
    0x7946AC23: "uShadow::SHADOW_MAP_TYPE",
    0x79478204: "XGI_SESSIONMODIFYSKILL_MSG",
    0x79484087: "_iobuf",
    0x794A6D55: "COHER_BASE_HOST",
    0x794B4BCE: "CGM_MC1_IO_CNTL",
    0x7951ED1A: "_TIMER_TYPE",
    0x7959146A: "RB_PERFCOUNTER3_SELECT",
    0x795AA1D0: "CCalVideoMetadata",
    0x79638CF0: "PA_SU_PERFCOUNTER0_HI",
    0x7964E46C: "rEffect2D::E2D_PARTICLE_PRIM_COMMON",
    0x7967B843: "cOma016Action",  # pc-only
    0x796C362E: "sPrim::TEXTURE",
    0x796F9D13: "cEm30ActNeckBiteFinTH",  # pc-only
    0x79743B76: "_WIN32_FIND_DATAW",
    0x79765760: "D1SCL_SCALER_ENABLE",
    0x7985F7E8: "cEm52ActThrow",  # pc-only
    0x798A7521: "D3DVertexDeclaration",
    0x798B1677: "cOmJeepAction_om_act_dummy",  # pc-only
    0x798BB121: "_D3DPRIMITIVETYPE",
    0x798F8248: "PARAM_SC",
    0x79912804: "PCIEP_RESERVED",
    0x799E1EF6: "_FXLREGISTER_UPDATE",
    0x79A0C8FB: "uEffectEdit::LifeFrame",
    0x79A0E932: "CMp3Huffman",
    0x79A426BA: "CXStorageUploadParent::__vftable",
    0x79A56938: "_DVD_XGD2_DISC_AUTH_RESULT",
    0x79A5C87C: "_XNPXNKIDSECURITY",
    0x79AC4C05: "VC_PERFCOUNTER0_HI",
    0x79B3C04C: "cItAction_it_act_wait",  # pc-only
    0x79B3F7C4: "_DM_INPUT_BIND_AUTOMATION",
    0x79B52D60: "RB_BLENDCONTROL1",
    0x79BD9991: "cPlAction_pl_act_die_boatair",  # pc-only
    0x79BEFB3C: "uOm0026::cActStartL",  # pc-only
    0x79C4D475: "MtAABB",
    0x79C7A3F7: "cOmBoatAirAction_pl_act_damage_chafe",  # pc-only
    0x79C83584: "GC_ADAPTER_ID",
    0x79C8DB36: "AHEffectWind",  # pc-only
    0x79CA3BFD: "PA_SU_PERFCOUNTER1_SELECT",
    0x79CA97B6: "_XPROFILE_VOICE_THRU_SPEAKERS_OPTIONS",
    0x79CB5230: "CPnsInterChannelData",
    0x79CB8179: "_D3DBLENDOP",
    0x79CFCD85: "CXLiveAsyncTask",
    0x79D14E38: "sCapture::MOTIONBLUR",
    0x79D2B244: "cPlAction_pl_act_item_load_first",  # pc-only
    0x79D2F0F3: "_IMAGE_DEBUG_MISC",
    0x79D3E5EE: "cEm20ActDmgHoldCeil",  # pc-only
    0x79D81560: "sCollision::RadixSort::__vftable",
    0x79DA6B49: "CCalHttpStream::HttpCallbackInfo",
    0x79E1D9FD: "cEm20ActAtkComboExtTate",  # pc-only
    0x79E1EC7C: "uEffectEdit::CHAIN_STATUS",
    0x79E37F4D: "DEPENDREC",
    0x79E38FD1: "cPlAction_pl_act_damage_common",  # pc-only
    0x79E7AAA4: "rEffectSetData::PRIM_MODEL_TYPE",
    0x79ED4A0D: "DRRMPDDATE",
    0x79F05E3D: "GC_PMI_CAP_ID",
    0x79F14303: "_XCONTENT_SIGNATURE",
    0x79F6F48B: "_XMSG_PROPERTY_BINARY",
    0x79FDA3EF: "_FP_80",
    0x7A005F7C: "_XMSG_GAME_INVITE_GET_ACCEPTED",
    0x7A0C6BAC: "AZ0_LOOPBACK_LFSR",
    0x7A219E6F: "_XEX_DELTA_PATCH_DESCRIPTOR",
    0x7A23A3A8: "rEffectSetData::ESD_PARAM_PLACE",
    0x7A2D1C0E: "D3D::AsyncResourcesPhysicalData",
    0x7A2EE899: "XONLINE_TITLE_ENUMERATE_FLAGS",
    0x7A32158C: "cEm83ActDieBlow",  # pc-only
    0x7A38BFF4: "rEffectList::EFL_KEYFRAME_COMMON",
    0x7A38D3D4: "cEm22ActDmg",  # pc-only
    0x7A40EAEB: "uOm0026::cActWaitR",  # pc-only
    0x7A448ABE: "FSB_LX_DEBUG_HI_AND",
    0x7A475B22: "_XSTORAGE_UPLOAD_FROM_MEMORY_PARAMS",
    0x7A489BC1: "EFC_TRAIT",
    0x7A48CCFE: "TP1_CHICKEN",
    0x7A4CF03B: "XNetStartupParams",
    0x7A50694B: "cEm3401Action",  # pc-only
    0x7A5A0DC6: "XUIMessageSoundVolume",
    0x7A5F69E2: "_XLIVEBASE_ASYNC_MESSAGE",
    0x7A6025FB: "rEffect2D::MyDTI",
    0x7A606F10: "aViewer",  # pc-only
    0x7A611B02: "_D3DCUBEMAP_FACES",
    0x7A65D61E: "cAITerrainHeightAnalyzer",  # pc-only
    0x7A686683: "rEffectList::EFL_PARAM_LINE_FIX_END",
    0x7A691948: "_WMAFormat",
    0x7A692399: "_LD_DEMO",
    0x7A704CE2: "cEm6dActErase",  # pc-only
    0x7A715B4F: "D1OVL_SURFACE_OFFSET_X",
    0x7A761923: "IMPORT_OBJECT_NAME_TYPE",
    0x7A77CFE7: "SQ_FETCH_RT_3",
    0x7A79BA83: "cEm43ActRageEnd",  # pc-only
    0x7A7D5E52: "cEm40ActBeatDownF",  # pc-only
    0x7A7DB8D5: "cPlAction_pl_act_damage_stunrod",  # pc-only
    0x7A80486C: "PCIE_HW_DEBUG",
    0x7A8135D7: "_XE_RSA_KEY_TYPE",
    0x7A818657: "CXuiTextElement",
    0x7A836B83: "VGT_EVENT_INITIATOR",
    0x7A853719: "_HEAP_SEGMENT",
    0x7A8751B8: "AZ0_RESET_CRC_COUNTERS",
    0x7A88B67B: "uScrModelUV",  # pc-only
    0x7A908CFC: "uRefWater::__vftable",
    0x7A9A7000: "uAdhesion::ADHESION_NODE_HEADER",
    0x7A9A76AE: "uAdhesion",
    0x7A9C8733: "sUnit::MoveLine::MyDTI",
    0x7A9F0EAF: "uEffectVFR::STRIP_WORK",
    0x7A9F7EE5: "cEm52ActDie",  # pc-only
    0x7AA02BF7: "sRender::MyDTI",
    0x7AA4A1C4: "cOmCoopDoorAction_om_act_dummy",  # pc-only
    0x7AA8CE21: "_FILE_FS_OBJECTID_INFORMATION",
    0x7AA95C1F: "D3D::PIX_VIDEO_HEADER",
    0x7AAA6C93: "cAIFSM::ParamConstString",  # pc-only
    0x7AAC90A3: "_XMEDIA_VIDEO_FRAME",
    0x7AAE8C86: "uEffectEdit::MovePathChain",
    0x7AB10828: "_D3DRING_BUFFER_PARAMETERS",
    0x7AB4B1A6: "TCF_PERFCOUNTER5_HI",
    0x7ABA3C93: "HSIO_PHASE_INIT",
    0x7ABC0AFC: "cEm84CoreActStripped",  # pc-only
    0x7ABEC63D: "_STRING_VERIFY_RESPONSE",
    0x7AC25226: "_XAM_XALLOC_ALLOCATOR_IDS",
    0x7AC2DB17: "uOmLoadItem::cActWait",  # pc-only
    0x7AC43E6C: "XAUDIOSOURCEFXINIT",
    0x7AC56C5C: "IShaderPDBBuilder",
    0x7AC6C733: "cEm45ActWait",  # pc-only
    0x7AD2BB8C: "_DXVA_MVvalue",
    0x7AD4F23E: "CP_NV_FLAGS_3",
    0x7AD567B0: "uFishEyeFilter",
    0x7AD97D5A: "AZ0_SECONDARY_STATE_DWORD1",
    0x7ADAC87A: "DC_TEST_DEBUG_DATA_TRIGGER_PATTERN",
    0x7ADAF1FC: "cPlAction_pl_act_attack_knee_bazooka_turn_b",  # pc-only
    0x7ADBD6AE: "MC1_CNTL",
    0x7ADFDF20: "cTrans::ARRAY_HEADER",
    0x7AE657A2: "sCollision::cColTree::MyDTI",
    0x7AE7C099: "ID3DXEffectCompiler",
    0x7AEA4AA9: "SubFrameConfigInfo",
    0x7AEB93F7: "LOMList",  # pc-only
    0x7AEC09A5: "REG_MACRO_ADDR_6",
    0x7AEC8590: "VFNT_VOICEFONT_BLOCK",
    0x7AEEC756: "sResource::LOADING_INFO",
    0x7AF10EC7: "cEmc2ActDownEnd",  # pc-only
    0x7AF6DD1F: "cFSMOrderEm10::FuncParamSetAction_Em10",  # pc-only
    0x7AF80550: "_MARKETPLACE_COUNTS_USER_CACHE",
    0x7AFF661A: "cOmLockActWait",  # pc-only
    0x7B03CE5E: "SurfaceSwap",
    0x7B04C9AA: "_FILE_FS_VOLUME_INFORMATION",
    0x7B0A1B64: "cEm83ActReadyBgn",  # pc-only
    0x7B122630: "cEmc2ActOff",  # pc-only
    0x7B13817E: "uOmCoopSwitch_S301::cActAnother",  # pc-only
    0x7B15837F: "ThreadCtl",
    0x7B174104: "uMovie::Player",
    0x7B1B1A23: "cEmc4Action",  # pc-only
    0x7B1C56FD: "_XUSER_RANK_REQUEST",
    0x7B1C8F1D: "cOm0200EvActPlDie",  # pc-only
    0x7B1EABA1: "RTS_EDGE_1_DY",
    0x7B1F4BA2: "_currencyfmtW",
    0x7B203A12: "_HVSTATS_CORE",
    0x7B21C06C: "RB_SURFACE_INFO",
    0x7B230195: "rEffectList::CLOTH_CURVE_OPTION_FLAG",
    0x7B238783: "rShape::SHAPE_KEY",
    0x7B29D034: "CP_RT4_BADR",
    0x7B2C9FBF: "XUINotifyPress",
    0x7B302E21: "uOmCoopTreasure::cActPlOpened",  # pc-only
    0x7B31A3D1: "XAUDIO::CEffectManager",
    0x7B357444: "CP_PFP_RT_UCODE_ADDR",
    0x7B367EE5: "_KD_SYMBOLS_INFO",
    0x7B38741E: "cEm62ActErase",  # pc-only
    0x7B5B6A0C: "_PM4CMDSETCONSTANT",
    0x7B5B6C27: "uWeaponSub",  # pc-only
    0x7B637D10: "aS200::cActPlBase",  # pc-only
    0x7B63B3C5: "_DISPATCHER_HEADER",
    0x7B68A9E1: "uOmExplosive_Fell::cActWait",  # pc-only
    0x7B7138D9: "rAIFSMParameter",  # pc-only
    0x7B754420: "_KPRCB",
    0x7B806A6A: "rConfig",
    0x7B81795C: "cAnimVector3",  # pc-only
    0x7B8361C2: "sCollision::COLLIDER_CONTACT_TYPE",
    0x7B885BC4: "HSIO_PHASE_CAPTURE",
    0x7B88E483: "cPlAction_pl_act_weapon_ready_loop",  # pc-only
    0x7B92638D: "sResource::RemoteInfo",
    0x7B932BD9: "D3D::CMicrocodeBuilder::Microcode::AnalyzeCodeVisitorContext",
    0x7B975948: "XAUDIO::SRC::Common",
    0x7B977979: "IOC_PERFCOUNTER2_LOW",
    0x7B9947B9: "VGT_GRP_PRIM_TYPE",
    0x7BA01107: "_STRING_V1_TITLE_ID_REQUEST",
    0x7BA1E4CB: "_DXVA_COPPStatusDisplayData",
    0x7BA87A04: "CP_RT0_POLL_ADDRESS",
    0x7BA88F1E: "cEm45ActTackle",  # pc-only
    0x7BA8C7AA: "CXUpdateDownload",
    0x7BAB6E32: "rEffectList::MODEL_ANIM_FLAG",
    0x7BB045B6: "CStreamInfo",
    0x7BB2BD61: "PCIE_RX_LASTACK_SEQNUM",
    0x7BB66FED: "tagCpyCtrl",
    0x7BB7346C: "CODEC_TYPE",
    0x7BBB9B5F: "rCloth::Chain::ChainType",
    0x7BBC2BBB: "HSIO_PHASE_OUT",
    0x7BBF5CB0: "rAIDynamicLayout",  # pc-only
    0x7BBF90D3: "cEmc2ActDamageCamera",  # pc-only
    0x7BC82168: "_XSESSION_VIEW_PROPERTIES",
    0x7BCB416C: "cPlAction_pl_act_die_syokei_lie",  # pc-only
    0x7BCC756A: "CP_D1_EOL_SOF_COUNTER",
    0x7BD1A7DC: "sBioVibration",  # pc-only
    0x7BD40C22: "cEm70ActWalk",  # pc-only
    0x7BD6BF27: "_RTL_HEAP_PARAMETERS",
    0x7BD78E5E: "cEm61ActCaw",  # pc-only
    0x7BD863C2: "XONLINE_MUTELIST_USER_INTERNAL",
    0x7BD876B3: "tagWMCNewIndex",
    0x7BDBC26F: "AZ0_ZFAIL_SAMPLES",
    0x7BDCD6EC: "cEm43ActDamage",  # pc-only
    0x7BED4425: "_P_TEAM_RECRUIT_MSG_XUID",
    0x7BEDBFC0: "IXAudioRenderEffectVtbl",
    0x7BEF14B2: "BSB_CONTROL",
    0x7BF3EF37: "_XUSAGE_ATTRIBUTE_TYPE",
    0x7BF4BC86: "cEm20ActAtkHangingAfter",  # pc-only
    0x7BFC16E3: "NetworkResolverXbox",
    0x7BFC187D: "AZ1_SECONDARY_STATE_DWORD1",
    0x7C027C74: "_D3DXERR",
    0x7C0353E8: "DelayedCopyFrame_Ctl",
    0x7C06AC83: "cEm83ActReady",  # pc-only
    0x7C089BD6: "_OBJECT_TYPE_LIST",
    0x7C0A7952: "uIdCredit00",  # pc-only
    0x7C0F0261: "IXuiDevice::__vftable",
    0x7C13D339: "uSynchroPointLight",
    0x7C172A92: "CP_ME_NRT_ADDR",
    0x7C17B6F5: "_STORAGE_DL_RESPONSE_BUFFER",
    0x7C198319: "cUnit::MyDTI",
    0x7C1B8F0D: "aS103::cActPlJumpOut",  # pc-only
    0x7C208D8F: "_CACHEFILETABLE",
    0x7C281903: "_HUD_PARAMS",
    0x7C2BE721: "CCalBase::ORIENTATION_MODE",
    0x7C2F5AD0: "cOmBoatAirAction_om_act_wait",  # pc-only
    0x7C30D21C: "D3DPixelShader",
    0x7C36907A: "XAUDIO::CExternCriticalSection",
    0x7C381DAA: "cPlAction_pl_act_wall_crouch_f_ready",  # pc-only
    0x7C3CB689: "BITDEPTH",
    0x7C3D9B39: "rClothXml::Index",
    0x7C4047D3: "MtFile",
    0x7C41D2A3: "D1SCL_CRC_LAST",
    0x7C470FCF: "_XMEDIA_VIDEO_SCREEN_VERTEX",
    0x7C4B9BD7: "_OBJECT_TYPE",
    0x7C4EC887: "AZ0_SFAIL_SAMPLES",
    0x7C4F6FB0: "RTS_WD_EDGE_2_DIST_LSBS",
    0x7C52005F: "SQ_PERFCOUNTER1_LOW",
    0x7C568887: "TP3_PERFCOUNTER1_SELECT",
    0x7C59CDE7: "sPhysics::ConstraintParam",
    0x7C5B8B09: "_XCOMPRESS_FILE_HEADER_LZXTDECODE",
    0x7C5EFC98: "NetworkCommunity::Chat",
    0x7C5F920A: "tagBITMAPINFO",
    0x7C63F600: "uOmCoopSwitch_S301::cActBase",  # pc-only
    0x7C65CBD0: "_HAL_HDDVD_ROM_REGISTRATION",
    0x7C6BFC28: "XNOTIFICATION_USER",
    0x7C70E3E9: "_OFFER_PURCHASE_GAMERTAG_RESPONSE",
    0x7C737E98: "XAUDIOFXINFO",
    0x7C7D1B31: "cEmAction_pl_act_attack_throw",  # pc-only
    0x7C823AAD: "cEm20ActAtkTate",  # pc-only
    0x7C85D6C8: "XGCpuVertexShader",
    0x7C8AA745: "_BANNER_GET_LIST_REQUEST",
    0x7C8B0681: "MtCollada::Array::TYPE",
    0x7C8BB25F: "RBBM_INT_STATUS",
    0x7C91AA50: "IDirectXFileEnumObject::__vftable",
    0x7C91DC64: "AZ1_SECONDARY_STATE_DWORD5",
    0x7C953A58: "cJointTwist",  # pc-only
    0x7C9974BE: "TP2_DEBUG",
    0x7C9C13FB: "uOmJoke::cActWait",  # pc-only
    0x7CA5DB1E: "D1CRTC_STEREO_CONTROL",
    0x7CA7CE3E: "D3DXVECTOR3",
    0x7CAA0CEC: "GpuRepeatpad",
    0x7CAF605C: "cTrans::MODE",
    0x7CB523AD: "uOmCoopTreasure::cActWait",  # pc-only
    0x7CC11B50: "cEm32PlEvent_PreCounter",  # pc-only
    0x7CC3DB0F: "_FILE_STREAM_INFORMATION",
    0x7CC484A7: "uOmCoopJumpBroad::cActWait",  # pc-only
    0x7CC69C76: "SXIFCCG_DEBUG_REG0",
    0x7CC867A2: "AZ1_LOOPBACK_PATTERN2PHS2",
    0x7CC9BAF6: "PA_SC_DEBUG_CW_1",
    0x7CCB602A: "_IO_STACK_LOCATION",
    0x7CCB6F37: "_DXVA_NominalRange",
    0x7CDA15B3: "SQ_INSTRUCTION_CF_JMP_CALL_2",
    0x7CDA2243: "cEm84ActAtckSliding",  # pc-only
    0x7CDDC1D7: "cFSMOrder::FuncParamVector3",  # pc-only
    0x7CDE034C: "GPU_SCREENEXTENT",
    0x7CDE52B0: "NetworkLayer::Filter",
    0x7CE2B9BD: "CP_RT11_COMMAND",
    0x7CE69759: "uOm095b_Cliff::cActPlFall",  # pc-only
    0x7CE71D02: "cEm32ActTongueRelease",  # pc-only
    0x7CE7DC63: "uOm1307_Boat::cActMove_E_End",  # pc-only
    0x7CE9011C: "_IO_COMPLETION_CONTEXT",
    0x7CEAE0C9: "XONLINE_BASIC_SUBSCRIPTION_INFO_FLAGS",
    0x7CF8DEA6: "rAIDynamicLayout::ObjPath",  # pc-only
    0x7CFB4ED0: "cEm34ActCrawl",  # pc-only
    0x7CFE0FF5: "cEm10ActAtkGunReload",  # pc-only
    0x7CFE89A7: "rModel::RCN_TABLE",
    0x7D00735F: "_AP21_MEASUREMENT_INPUT",
    0x7D068D6A: "_KPCR",
    0x7D06B84B: "HDMI_AUDIO_FORMAT",
    0x7D075AB5: "_CDROM_AUDIO_CONTROL",
    0x7D07E581: "GPUALUVECTOROP",
    0x7D0C08B5: "_WMID",
    0x7D109A4B: "cEm40ActBeatDownB",  # pc-only
    0x7D1530C2: "rSoundSourceMusic",
    0x7D1810B5: "uOm0934::cActBurning",  # pc-only
    0x7D187094: "DCCG_CLK_CNTL",
    0x7D1E223C: "_XEX_RAW_DATA_DESCRIPTOR",
    0x7D1ED113: "P_INVITE_REPLIES",
    0x7D21FE4A: "cShape::WeightNode::MyDTI",
    0x7D25A9D1: "MtCone",
    0x7D262C93: "CConcealmentInfo",
    0x7D2C887E: "uCloth::MyDTI",
    0x7D3324AC: "cEm83ActAtckKick",  # pc-only
    0x7D3455AA: "AZ0_MRU_BANK16_DEPTH_MASK",
    0x7D351D18: "uOma00f_UroPunch::cActBase",  # pc-only
    0x7D360B11: "_XCONTENT_DOWNLOADMEDIA_PARAMS",
    0x7D3D57C7: "VGT_GROUP_PRIM_TYPE",
    0x7D3D9D12: "std::ctype_base",
    0x7D3DFBE5: "FSB_LX_PMC2",
    0x7D3F6F3B: "rEffectAnimation::MyDTI",
    0x7D4041DF: "_ACCOUNT_GET_USER_TYPE_RESPONSE",
    0x7D46C38C: "MtCollada::Entry",
    0x7D4D6CB2: "cEm34ActDisrupted",  # pc-only
    0x7D4E2F25: "CXContentDownloadMedia::__vftable",
    0x7D4F4377: "MP4ObjectDescriptorMediaHeaderAtom",
    0x7D548869: "rEffectSetDataList::MyDTI",
    0x7D5540BB: "D1GRPH_Y_START",
    0x7D58D66B: "rCloth::__vftable",
    0x7D59B5CD: "XUIContentInfo",
    0x7D5FFB36: "tagCPanScanWindowInfo",
    0x7D60CE34: "CCalMediaMetadata",
    0x7D6F7816: "_HEAP_FREE_ENTRY_EXTRA",
    0x7D764649: "MP4ChunkLargeOffsetAtom",
    0x7D7894ED: "_HEAP_FREE_ENTRY",
    0x7D7E6D2E: "PA_CL_GB_HORZ_DISC_ADJ",
    0x7D810452: "ID01_DMIF_DCP_DATA_RETURN1",
    0x7D81CDBC: "REG_MACRO_ADDR_2",
    0x7D853CA6: "_XMARKETPLACE_TABLE",
    0x7D89FE11: "XUIContentDims",
    0x7D8AB8FE: "PIX_TITLE_OPTIONS",
    0x7D97AF54: "OBJECTHANDLER",
    0x7D97DFF4: "cWpAction_wp30_act_light_drop",  # pc-only
    0x7D9935CA: "uCoord",
    0x7D9935FF: "_KUSER_MODE_PDE",
    0x7D9ED899: "MtGeomConvex::MyDTI",
    0x7DA0EFB1: "_VESA_DETAILED_TIMING",
    0x7DA3BAFC: "SCRATCH_UMSK",
    0x7DA5BCCA: "rSoundSpeakerSetXml::COORDINATE",
    0x7DA9187B: "rEffectList::FORCE_TYPE",
    0x7DAA04D0: "BRTFILESEEKSTATE",
    0x7DAACCF6: "CodecVersion",
    0x7DAFB10E: "uOmWallStick::cActWait",  # pc-only
    0x7DB195AF: "D3D::CCapture::HashMap::ENTRY",
    0x7DB1E8E3: "IStreamVtbl",
    0x7DB22D1C: "cEm0cActDieExplosion",  # pc-only
    0x7DB4B943: "AZ0_SECONDARY_STATE_DWORD5",
    0x7DB4FE86: "sPad",
    0x7DB9D7FC: "_D3DXSHADER_CONSTANTTABLE",
    0x7DBB478F: "sPhysics::MassParticle",
    0x7DBDA29A: "CP_RT7_BADR",
    0x7DBE03DA: "cPlAction_pl_act_wall_crouch_turn_r",  # pc-only
    0x7DC1E183: "AZ0_BC2AZ_CRC_READ",
    0x7DC74914: "_XCONFIG_IPTV_SETTINGS",
    0x7DCF7C47: "NetworkConnection",
    0x7DCFD16F: "D1CRTC_FRAME_RESET_CONTROL",
    0x7DD03921: "uOmElevator::cActBase",  # pc-only
    0x7DD6F508: "uOmExplosive_Fell::cActFall",  # pc-only
    0x7DD7D2EC: "_OBJECT_DIRECTORY_INFORMATION",
    0x7DDDBD17: "MtGeomTriangle::MyDTI",
    0x7DE27B92: "uColorCorrectFilter::MyDTI",
    0x7DE2F311: "AZ1_MRU_BANK17_DEPTH_MASK",
    0x7DE3D6D4: "AIFFINSTRUMENT",
    0x7DE456A7: "KEYS",
    0x7DE5398C: "_HAL_BKGD_MODE_REGISTRATION",
    0x7DE9EF66: "PIX_REQUEST_GET_CAPTURE",
    0x7DEB844C: "DC_LUTA_CONTROL",
    0x7DF56E19: "cTrans::VolumeTexture::MyDTI",
    0x7DF88B30: "sResource::MODE",
    0x7DFF108A: "XAUDIO::XAUDIOFXMGRFXTABLE",
    0x7E01E048: "PRIOTITY",
    0x7E084911: "cEm0cPlEvent_Release",  # pc-only
    0x7E0A2804: "sResource::RESOURCEWORK",
    0x7E0D5C15: "cFSMOrder::FuncParamSetEnemy",  # pc-only
    0x7E0FD0F1: "cEm10ActFall",  # pc-only
    0x7E1017C6: "_XSWAPDISC_ERROR_TEXT",
    0x7E10E3B0: "cPlAction_pl_act_bump_up",  # pc-only
    0x7E14D2E0: "wmaudio2waveformat_tag",
    0x7E15AE88: "_XONLINE_SCHEMA_DATA",
    0x7E199640: "aS109::cActJeepRestart",  # pc-only
    0x7E19B697: "ID03_DMIF_DCP_DATA_RETURN3",
    0x7E1AFA4E: "_CRACKEDPATH",
    0x7E1B6966: "PatConnection::Server",
    0x7E1C48B2: "AZ0_MRU_DEPTH_MASK",
    0x7E1D866F: "cTrans::VIEWPORT",
    0x7E1F9DBF: "ID3DXAllocateHierarchyVtbl",
    0x7E23897A: "princeton_digital::lowpass_t",
    0x7E310198: "XUIMessageInput",
    0x7E326ED5: "AZ0_MRU_BANK12_DEPTH_MASK",
    0x7E33A16C: "rSoundPackage",
    0x7E350727: "rConfig::GROUP",
    0x7E36894E: "BIF_PERFCOUNTER0_SELECT",
    0x7E389698: "tPAYLOAD_MAP_ENTRY_EX",
    0x7E3BF3E1: "EP_CAPABILITIES_PTR",
    0x7E3CFFEA: "CP_RT9_MASK",
    0x7E3DCC96: "uCapsuleShadowLight",
    0x7E3E2CFB: "LICSTOREOBJ",
    0x7E3FE6C8: "MtMatrix",
    0x7E4548A3: "_RAM_FILE_UNIT",
    0x7E46F906: "_XSESSION_MEMBER",
    0x7E475D53: "PatInterface::Nickname",
    0x7E4FBE9D: "CP_RT15_SIZE",
    0x7E52E4CF: "TCB_FETCH_GEN_WALKER_DEBUG",
    0x7E553472: "MtPreProcessor::DefaultInclude",
    0x7E579BE7: "_D3DXMESHDATA",
    0x7E625C24: "VC_DEBUG_DATA",
    0x7E673841: "JITTERBUF",
    0x7E675EF9: "_PHONE_INFO",
    0x7E690B77: "_PHYSICAL_MEMORY_RUN",
    0x7E6BFB41: "IStream::__vftable",
    0x7E6C235B: "NetworkCommunityPat",
    0x7E6E142B: "XAMINSTRUMENTATION_SOURCE_CONFIG",
    0x7E6F0FD9: "rEffectList::EFL_PARTICLE_PRIM_COMMON",
    0x7E7390EF: "cAnimVector3::Key",  # pc-only
    0x7E74DEE7: "NetworkXboxMediator::RichPresence",
    0x7E756B23: "XG_MCT::CXEncoder",
    0x7E75E339: "ID3DXPMesh",
    0x7E7605BF: "rAIDynamicLayoutXml",  # pc-only
    0x7E76F696: "SQ_FETCH_0",
    0x7E7AB237: "XAUDIO::CStdFileStream",
    0x7E8014B0: "uCascadeLSM",
    0x7E824569: "_D3DVSHADERCAPS2_0",
    0x7E8B9070: "PMI_STATUS_CNTL",
    0x7E926D80: "DC_TEST_DEBUG_OUT_PIN_MASK",
    0x7E9A25F7: "_XSTORAGE_ENUMERATE_REQUEST",
    0x7E9CFDE1: "cEm80ActSyutoDie_PL",  # pc-only
    0x7E9DD8F7: "_XGET_REVOCATION_LIST_REPLY",
    0x7E9EFF01: "uEffectEdit::MassBillboard",
    0x7EA0A8AB: "rGridEnvLight::NativeBoxInfo",
    0x7EA166EA: "cEm20ActAtkHangingSkewer",  # pc-only
    0x7EA200BF: "XAM_DEFAULT_IMAGE_ID",
    0x7EAA43AE: "cEm20ActAtkCombo2",  # pc-only
    0x7EAA7BBB: "_XMSG_GAMEINVITE_ANSWER_INFO",
    0x7EAAE662: "Allocation_type",
    0x7EADFE36: "HRSRC__",
    0x7EB03262: "MC1_BSB_SNOOPED_TIMER_CNTL",
    0x7EB2DCCC: "AZ0_LOOPBACK_PATTERN2PHS1",
    0x7EBF8139: "uOm0201_Piano::cEventActFailed",  # pc-only
    0x7EC2172B: "GC_HEADER",
    0x7EC2C547: "DC_GPIO_XDVODATA_EN",
    0x7ECBA87B: "_BACKGROUND_DOWNLOAD_ITEM",
    0x7ECCACA7: "XECRYPT_DES_STATE",
    0x7ED4C86C: "rSoundEngineXml",  # pc-only
    0x7ED4F347: "sMouse::TYPE",
    0x7ED5FDA6: "sShader::FILTER_TYPE",
    0x7EE20D40: "_BUFFERCACHE",
    0x7EE4C86E: "AZ1_MRU_BANK13_DEPTH_MASK",
    0x7EE6DEB4: "_DUMP_BASIC_SERVICES",
    0x7EE7C0D0: "PA_SC_PERFCOUNTER3_LOW",
    0x7EE93C84: "CXUpdateDownload::REFERRAL_RESPONSE_BUFFER",
    0x7EEB266F: "RB_HSIO_CALIBRATE",
    0x7EEC4146: "uOm0927_Crane::cActMoveAC",  # pc-only
    0x7EEFF27F: "_XALLOC_ALLOCATOR_IDS",
    0x7EF08CAF: "cAIBlackBoard",  # pc-only
    0x7EF82ACC: "MtCollisionEpa::MtEpaLocalAllocator",
    0x7EF98E67: "SCHEMA_ARGUMENT_INFO",
    0x7EFE4302: "_IMAGE_RESOURCE_DIRECTORY",
    0x7F0124C6: "IXUIRuntimeHooks",
    0x7F02C785: "cEm61ActDestFly",  # pc-only
    0x7F05FE02: "std::bad_exception",
    0x7F0B1469: "CP_RT5_POLL_ADDRESS",
    0x7F0BA0A1: "CListEntry",
    0x7F0D3025: "MP4FreeSpaceAtom",
    0x7F0D9789: "CSharedResource",
    0x7F0ED790: "PCIE_P_STR_CNTL_UPDATE",
    0x7F0FEB5C: "sCollision::PROFILE_ID",
    0x7F14C403: "CP_ME_PS_EVENT_SRC",
    0x7F151759: "sSoundN::Voice::VOICE_TYPE",
    0x7F16771C: "InputModifier",
    0x7F1A6828: "_D3DPERFCOUNTER_VALUES",
    0x7F1B85AF: "cEm83PlEvent_PinionDmg",  # pc-only
    0x7F224D83: "rPathList::PathInfo",  # pc-only
    0x7F2579B7: "EFC_PARAM_ANGLE",
    0x7F2F3E7B: "_D3DXPATCHMESHTYPE",
    0x7F2FA466: "sMain::__vftable",
    0x7F329990: "rCollada::MyDTI",
    0x7F3C2292: "BIU_IOC_SLV_ORDER_CNTL",
    0x7F3C9140: "PCIE_VC0_CAP_REG1",
    0x7F4151A9: "_PASSPORT_GET_SECRET_QUESTION_RESPONSE",
    0x7F42C648: "cEm10ActAtkPlagaSmash",  # pc-only
    0x7F473EA1: "uMotionCamera::FOV_TYPE",
    0x7F4C6E0B: "cEm10ActAtkSitGunAim",  # pc-only
    0x7F4DC844: "NetworkRanking::Attach",
    0x7F4E5419: "OPTIMIZATIONFOCUS",
    0x7F4FB130: "VGT_MULTI_PRIM_IB_RESET_INDX",
    0x7F50B802: "uToneMapControl::MyDTI",
    0x7F52F807: "_PARTITION_INFORMATION",
    0x7F5AA97E: "rBioBgmMap::BGM_ENTRY",  # pc-only
    0x7F5C47EB: "cOmExplosiveEventPL",  # pc-only
    0x7F5D5596: "MtHeapArray::MyDTI",
    0x7F5DE408: "_woutput_l::__l72::_count_string",
    0x7F62BE08: "_EXCEPTION_POINTERS",
    0x7F65D0AA: "MtFile::FileInfo::ATTR",
    0x7F6D23D0: "uFacial::MyDTI",
    0x7F6FB807: "uNavMeshNodePickUp::PickUpBit",  # pc-only
    0x7F70A719: "ImageArray",
    0x7F73E1D0: "sSoundN::EQ_PARAMETER",
    0x7F744648: "FSB_TX_TERST_XSTP",
    0x7F749135: "PCIE_PERF_LATENCY_COUNTER0",
    0x7F7AA3DA: "uEffectEmitter::CAMERA_CONST_TYPE",
    0x7F7D18A4: "DO_TEST_DEBUG_EDGE_TRIGGER_MASK",
    0x7F803B63: "cEm44ActStamp",  # pc-only
    0x7F8AC70C: "NetworkQueue",
    0x7F8B88DD: "sCollision::HIT",
    0x7F8C4B80: "uEffectEdit::Particle",
    0x7F8D2D67: "XNOTIFICATION_DEQUEUE",
    0x7F903781: "uEffectEdit::Texline",
    0x7F943573: "_D3DVS_ADDRESSMODE_TYPE",
    0x7F94DC6E: "RB_AZ1_BC_CRC",
    0x7F955745: "MC0_BSB_SNOOPED_TIMER_CNTL",
    0x7F9A6D4D: "rMotion::MOTION_HDR",
    0x7F9DEBDF: "NetworkMutex::__vftable",
    0x7F9FFBB7: "XCOMPRESS::LCI_CONTEXT",
    0x7FA08048: "DC_PERFCOUNTER1_SELECT",
    0x7FA18D77: "_PAYMENT_INSTRUMENT_INFO",
    0x7FA30FE5: "_Q_SEND_MESSAGE_MSG_INTERNAL",
    0x7FA8A62E: "CP_ST_BASE",
    0x7FA8FC89: "D3DCommandBuffer",
    0x7FADB78A: "cEm83ActFire",  # pc-only
    0x7FB4E4EE: "tagWMVPictureInfo",
    0x7FB85568: "_XSTORAGE_FACILITY",
    0x7FB9891A: "sSoundN::ExternalVoice::__vftable",
    0x7FBACF6D: "D3DXShader::CNodeVariable",
    0x7FBB1A91: "uEffectEdit::CHAIN_WORK",
    0x7FBB5F56: "NB_CAPABILITIES_PTR",
    0x7FC77C0F: "XpsGlobal",
    0x7FC8153E: "princeton_digital::delay_t",
    0x7FC99EB9: "D3D::QueueRecord_Initialize",
    0x7FCD6773: "DEVICE_CNTL",
    0x7FCEBDA0: "cEm70ActBoxAttack",  # pc-only
    0x7FCF4E0D: "RunLevelStatus",
    0x7FD178C5: "_XMXICO4",
    0x7FD26AD9: "cEm20ActAtkHanging_PL",  # pc-only
    0x7FD3A26A: "uOmCrouch::cActCrouch",  # pc-only
    0x7FD42E8A: "cShape::WeightNode::STATE",
    0x7FD6CCA7: "sSoundN::CONTROL_TYPE",
    0x7FDB1EEA: "IOC_CNTL",
    0x7FE163C4: "cEm32PlEvent_MountHold",  # pc-only
    0x7FE1C0C5: "cFSMAct",  # pc-only
    0x7FE624C8: "_ENUMERATE_GENRES_RESPONSE",
    0x7FE8D256: "sVibration::__vftable",
    0x7FEA8EC5: "cEm30ActAtckTentacle",  # pc-only
    0x7FEC9049: "D1CRTC_STATUS_FRAME_COUNT",
    0x7FED83DF: "_PIX_AUTOMATION_MESSAGE_ID",
    0x7FEEEFC5: "cEm65ActBoxAttack",  # pc-only
    0x7FEF9F56: "cPlAction_pl_act_damage_blow_l",  # pc-only
    0x7FF0697A: "sMouse::BUTTON",
    0x7FF19311: "sResource::Iterator",
    0x7FFE5835: "_GET_POINTS_BALANCE_REQUEST",
    0x7FFE87E2: "PCIE_P_PAD_MISC_CNTL",
    0x430B4FF4: "rPathList",  # used
    0x60DD1B16: "rLayoutSpr",  # used
    0x16C2D639: "cSetInfoItem",
    0x58F29ED8: "cItemSetInfo",
    0x04EE4467: "cSetInfoEm10",
    0x0C9ED9BC: "cSetInfoEnemy",
    0x155F7352: "cSetInfoOmLadderV",
    0x221E64CE: "rSoundSeGenerator::LayoutInfo",
    0x25A1B38C: "cSetInfoEm62",
    0x2DAE9CFF: "sLightLinker::LightLink",
    0x2ECAC50E: "cSetInfoInsModel",
    0x38F66FC3: "rSoundSeGenerator",
    0x446ECFAD: "AHShapeBoxRotate",
    0x5898749C: "rBioBgmMap",
    0x5BBE5DF2: "cSprite",
    0x66B45610: "rAIFSM",
    0xFF000000: "Junk???",
}

SDL_DTI_HASHES = {
    "dmc4": DTI_DMC4,
    "re5": DTI_RE5
}
