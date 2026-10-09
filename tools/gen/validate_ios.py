import plistlib, json, glob, os, sys
import xml.etree.ElementTree as ET
from PIL import Image
B = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ios/build/RollModel'
ok = True
def check(cond, msg):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg); ok = ok and cond
# 1. project file parses and is wired up
from pbxproj import XcodeProject
p = XcodeProject.load(B + '/RollModel.xcodeproj/project.pbxproj')
tg = p.objects.get_targets()
check(len(tg) == 1 and tg[0].name == 'RollModel', 'one app target')
t = tg[0]
phases = [p.objects[x] for x in t.buildPhases]
names = [ph.isa for ph in phases]
check(names == ['PBXSourcesBuildPhase', 'PBXFrameworksBuildPhase', 'PBXResourcesBuildPhase'], 'build phases ' + str(names))
def files(ph): return sorted(p.objects[p.objects[bf].fileRef].path for bf in ph.files)
src = files(phases[0]); res = files(phases[2])
check(src == sorted(['AppDelegate.swift', 'SceneDelegate.swift', 'GameViewController.swift', 'GameSchemeHandler.swift', 'HapticsBridge.swift', 'DeviceBridge.swift']), 'sources ' + str(src))
check(res == ['Assets.xcassets', 'Game', 'PrivacyInfo.xcprivacy'], 'resources ' + str(res))
# every file reference points at something that exists on disk
grp = p.objects[p.objects[p.rootObject].mainGroup]
missing = []
def walk(g, base):
    for c in g.children:
        o = p.objects[c]
        path = os.path.join(base, getattr(o, 'path', '') or '')
        if o.isa == 'PBXGroup': walk(o, path)
        elif o.isa == 'PBXFileReference' and o.sourceTree == '<group>' and not os.path.exists(path): missing.append(path)
walk(grp, B)
check(not missing, 'all file references exist ' + str(missing))
for cfgid in p.objects[t.buildConfigurationList].buildConfigurations:
    c = p.objects[cfgid]; bs = c.buildSettings
    check(bs['PRODUCT_BUNDLE_IDENTIFIER'] == 'studio.primeshots.rollmodel' and bs['INFOPLIST_FILE'] == 'RollModel/Info.plist' and bs['ASSETCATALOG_COMPILER_APPICON_NAME'] == 'AppIcon', 'target settings ' + c.name)
    check(os.path.exists(os.path.join(B, bs['INFOPLIST_FILE'])), 'Info.plist path resolves (' + c.name + ')')
# 2. plists
info = plistlib.load(open(B + '/RollModel/Info.plist', 'rb'))
check(info['UIApplicationSceneManifest']['UISceneConfigurations']['UIWindowSceneSessionRoleApplication'][0]['UISceneDelegateClassName'] == '$(PRODUCT_MODULE_NAME).SceneDelegate', 'scene delegate class')
check(info['ITSAppUsesNonExemptEncryption'] is False and info['UILaunchScreen']['UIColorName'] == 'LaunchBackground', 'encryption flag and launch screen')
plistlib.load(open(B + '/RollModel/PrivacyInfo.xcprivacy', 'rb')); plistlib.load(open(B + '/RollModel.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist', 'rb'))
check(True, 'privacy manifest and workspace plist parse')
# 3. xml
sch = ET.parse(B + '/RollModel.xcodeproj/xcshareddata/xcschemes/RollModel.xcscheme').getroot()
ids = {e.get('BlueprintIdentifier') for e in sch.iter('BuildableReference')}
check(ids == {t.get_id()}, 'scheme points at the target ' + str(ids))
check(sch.find('ArchiveAction').get('buildConfiguration') == 'Release', 'archive uses Release')
ET.parse(B + '/RollModel.xcodeproj/project.xcworkspace/contents.xcworkspacedata'); check(True, 'workspace xml parses')
# 4. asset catalog
for f in glob.glob(B + '/RollModel/Assets.xcassets/**/Contents.json', recursive=True): json.load(open(f))
im = Image.open(B + '/RollModel/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png')
check(im.size == (1024, 1024) and im.mode == 'RGB', 'icon 1024 RGB, no alpha (%s %s)' % (im.size, im.mode))
# 5. swift syntax
import tree_sitter_swift as tss
from tree_sitter import Language, Parser
lang = Language(tss.language()); parser = Parser(lang)
for f in sorted(glob.glob(B + '/RollModel/*.swift')):
    tree = parser.parse(open(f, 'rb').read())
    errs = []
    def visit(n):
        if n.type == 'ERROR' or n.is_missing: errs.append((n.start_point, n.type))
        for c in n.children: visit(c)
    visit(tree.root_node)
    check(not errs, 'swift syntax ' + os.path.basename(f) + ('' if not errs else ' ' + str(errs[:4])))
print('ALL OK' if ok else 'PROBLEMS')
