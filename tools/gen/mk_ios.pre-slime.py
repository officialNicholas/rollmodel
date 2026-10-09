import os, re, json, shutil, hashlib, plistlib
from PIL import Image

SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
OUT = SP + '/ios/build/RollModel'
NAME = 'RollModel'
BUNDLE_ID = 'studio.primeshots.rollmodel'
if os.path.exists(SP + '/ios/build'): shutil.rmtree(SP + '/ios/build')
APP = OUT + '/' + NAME
GAME = APP + '/Game'
os.makedirs(GAME + '/fonts'); os.makedirs(GAME + '/licenses'); os.makedirs(GAME + '/music')

# ---------- the game, as a full offline page ----------
src = open('/home/claude/paint-the-canvas.html').read()
fonts = "<style>\n" + "@font-face{font-family:'Bowlby One';font-style:normal;font-weight:400;font-display:swap;src:url(fonts/bowlby-one-latin-400-normal.woff2) format('woff2')}\n" + ''.join("@font-face{font-family:'Figtree';font-style:normal;font-weight:%d;font-display:swap;src:url(fonts/figtree-latin-%d-normal.woff2) format('woff2')}\n" % (w, w) for w in (600, 700, 800, 900)) + "html{-webkit-text-size-adjust:100%;text-size-adjust:100%}\n</style>"
n0 = len(src)
src, k = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">', fonts, src); assert k == 1
for a in ['<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>']:
    assert src.count(a) == 1; src = src.replace(a, '')
a = '<script src="three.r186.min.js">'; assert src.count(a) == 1; src = src.replace(a, '<script src="three.min.js">')
assert 'https://' not in re.sub(r"http://www\.w3\.org/2000/svg", '', src).replace('http://www.w3.org', ''), 'external URL left'
head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
'''
open(GAME + '/index.html', 'w').write(head + src.lstrip('\n') + '\n</html>\n')
NM = SP + '/node_modules'
shutil.copy(SP + '/t186/three.r186.iife.min.js', GAME + '/three.min.js')
# the recorded music: each an intro and a loop cut to the sample (the game fetches them from music/)
for f in sorted(os.listdir('/home/claude/music')):
    if f.endswith('.mp3'): shutil.copy('/home/claude/music/' + f, GAME + '/music/' + f)
shutil.copy(NM + '/@fontsource/bowlby-one/files/bowlby-one-latin-400-normal.woff2', GAME + '/fonts/')
for w in (600, 700, 800, 900): shutil.copy(NM + '/@fontsource/figtree/files/figtree-latin-%d-normal.woff2' % w, GAME + '/fonts/')
shutil.copy(SP + '/t186/node_modules/three/LICENSE', GAME + '/licenses/three.js-MIT.txt')
shutil.copy(NM + '/@fontsource/bowlby-one/LICENSE', GAME + '/licenses/BowlbyOne-OFL.txt')
shutil.copy(NM + '/@fontsource/figtree/LICENSE', GAME + '/licenses/Figtree-OFL.txt')

# ---------- Swift ----------
SWIFT = ['AppDelegate.swift', 'SceneDelegate.swift', 'GameViewController.swift', 'GameSchemeHandler.swift', 'HapticsBridge.swift', 'DeviceBridge.swift']
for f in SWIFT: shutil.copy(SP + '/ios/src/' + f, APP + '/' + f)

# ---------- Info.plist and privacy manifest ----------
info = {
    'CFBundleDevelopmentRegion': '$(DEVELOPMENT_LANGUAGE)',
    'CFBundleDisplayName': 'Roll Model',
    'CFBundleExecutable': '$(EXECUTABLE_NAME)',
    'CFBundleIdentifier': '$(PRODUCT_BUNDLE_IDENTIFIER)',
    'CFBundleInfoDictionaryVersion': '6.0',
    'CFBundleName': '$(PRODUCT_NAME)',
    'CFBundlePackageType': '$(PRODUCT_BUNDLE_PACKAGE_TYPE)',
    'CFBundleShortVersionString': '$(MARKETING_VERSION)',
    'CFBundleVersion': '$(CURRENT_PROJECT_VERSION)',
    'ITSAppUsesNonExemptEncryption': False,
    'LSRequiresIPhoneOS': True,
    'UIApplicationSceneManifest': {
        'UIApplicationSupportsMultipleScenes': False,
        'UISceneConfigurations': {'UIWindowSceneSessionRoleApplication': [{
            'UISceneConfigurationName': 'Default Configuration',
            'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate'}]},
    },
    'UIApplicationSupportsIndirectInputEvents': True,
    'UILaunchScreen': {'UIColorName': 'LaunchBackground'},
    'UIRequiredDeviceCapabilities': ['arm64'],
    'UIStatusBarHidden': True,
    'UIViewControllerBasedStatusBarAppearance': True,
    'UISupportedInterfaceOrientations': ['UIInterfaceOrientationPortrait'],
    'UISupportedInterfaceOrientations~ipad': ['UIInterfaceOrientationPortrait', 'UIInterfaceOrientationPortraitUpsideDown', 'UIInterfaceOrientationLandscapeLeft', 'UIInterfaceOrientationLandscapeRight'],
}
with open(APP + '/Info.plist', 'wb') as f: plistlib.dump(info, f, sort_keys=True)
priv = {'NSPrivacyTracking': False, 'NSPrivacyTrackingDomains': [], 'NSPrivacyCollectedDataTypes': [], 'NSPrivacyAccessedAPITypes': []}
with open(APP + '/PrivacyInfo.xcprivacy', 'wb') as f: plistlib.dump(priv, f, sort_keys=True)

# ---------- asset catalog ----------
AC = APP + '/Assets.xcassets'
os.makedirs(AC + '/AppIcon.appiconset'); os.makedirs(AC + '/AccentColor.colorset'); os.makedirs(AC + '/LaunchBackground.colorset')
info_xc = {'info': {'author': 'xcode', 'version': 1}}
json.dump(info_xc, open(AC + '/Contents.json', 'w'), indent=2)
ic = Image.open(SP + '/ios/icon_roller.png').convert('RGB'); assert ic.size == (1024, 1024)
ic.save(AC + '/AppIcon.appiconset/AppIcon-1024.png', optimize=True)
json.dump({'images': [{'filename': 'AppIcon-1024.png', 'idiom': 'universal', 'platform': 'ios', 'size': '1024x1024'}], **info_xc}, open(AC + '/AppIcon.appiconset/Contents.json', 'w'), indent=2)
def colorset(path, r, g, b):
    json.dump({'colors': [{'color': {'color-space': 'srgb', 'components': {'alpha': '1.000', 'blue': '0x%02X' % b, 'green': '0x%02X' % g, 'red': '0x%02X' % r}}, 'idiom': 'universal'}], **info_xc}, open(path + '/Contents.json', 'w'), indent=2)
colorset(AC + '/AccentColor.colorset', 0xE3, 0x12, 0x2F)
colorset(AC + '/LaunchBackground.colorset', 0x12, 0x0A, 0x24)

# ---------- Xcode project ----------
def oid(key): return hashlib.sha1(('rollmodel:' + key).encode()).hexdigest()[:24].upper()
I = {k: oid(k) for k in ['proj', 'g_main', 'g_app', 'g_prod', 'fr_app', 'fr_assets', 'fr_game', 'fr_plist', 'fr_priv', 'bf_assets', 'bf_game', 'bf_priv', 'src', 'fw', 'res', 'target', 'cl_p', 'cl_t', 'p_dbg', 'p_rel', 't_dbg', 't_rel'] + ['fr_' + f for f in SWIFT] + ['bf_' + f for f in SWIFT]}
assert len(set(I.values())) == len(I)

def q(v):
    v = str(v)
    return v if re.fullmatch(r'[A-Za-z0-9_./]+', v) else '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
def settings(d, ind='\t\t\t\t'):
    out = []
    for k in sorted(d):
        v = d[k]
        if isinstance(v, list): out.append(ind + k + ' = (\n' + ''.join(ind + '\t' + q(x) + ',\n' for x in v) + ind + ');')
        else: out.append(ind + k + ' = ' + q(v) + ';')
    return '\n'.join(out)

warn = {
    'ALWAYS_SEARCH_USER_PATHS': 'NO', 'ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS': 'YES',
    'CLANG_ANALYZER_NONNULL': 'YES', 'CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION': 'YES_AGGRESSIVE', 'CLANG_CXX_LANGUAGE_STANDARD': 'gnu++20',
    'CLANG_ENABLE_MODULES': 'YES', 'CLANG_ENABLE_OBJC_ARC': 'YES', 'CLANG_ENABLE_OBJC_WEAK': 'YES',
    'CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING': 'YES', 'CLANG_WARN_BOOL_CONVERSION': 'YES', 'CLANG_WARN_COMMA': 'YES', 'CLANG_WARN_CONSTANT_CONVERSION': 'YES',
    'CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS': 'YES', 'CLANG_WARN_DIRECT_OBJC_ISA_USAGE': 'YES_ERROR', 'CLANG_WARN_DOCUMENTATION_COMMENTS': 'YES',
    'CLANG_WARN_EMPTY_BODY': 'YES', 'CLANG_WARN_ENUM_CONVERSION': 'YES', 'CLANG_WARN_INFINITE_RECURSION': 'YES', 'CLANG_WARN_INT_CONVERSION': 'YES',
    'CLANG_WARN_NON_LITERAL_NULL_CONVERSION': 'YES', 'CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF': 'YES', 'CLANG_WARN_OBJC_LITERAL_CONVERSION': 'YES',
    'CLANG_WARN_OBJC_ROOT_CLASS': 'YES_ERROR', 'CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER': 'YES', 'CLANG_WARN_RANGE_LOOP_ANALYSIS': 'YES',
    'CLANG_WARN_STRICT_PROTOTYPES': 'YES', 'CLANG_WARN_SUSPICIOUS_MOVE': 'YES', 'CLANG_WARN_UNGUARDED_AVAILABILITY': 'YES_AGGRESSIVE',
    'CLANG_WARN_UNREACHABLE_CODE': 'YES', 'CLANG_WARN__DUPLICATE_METHOD_MATCH': 'YES', 'COPY_PHASE_STRIP': 'NO', 'DEAD_CODE_STRIPPING': 'YES',
    'ENABLE_STRICT_OBJC_MSGSEND': 'YES', 'ENABLE_USER_SCRIPT_SANDBOXING': 'YES', 'GCC_C_LANGUAGE_STANDARD': 'gnu17', 'GCC_NO_COMMON_BLOCKS': 'YES',
    'GCC_WARN_64_TO_32_BIT_CONVERSION': 'YES', 'GCC_WARN_ABOUT_RETURN_TYPE': 'YES_ERROR', 'GCC_WARN_UNDECLARED_SELECTOR': 'YES',
    'GCC_WARN_UNINITIALIZED_AUTOS': 'YES_AGGRESSIVE', 'GCC_WARN_UNUSED_FUNCTION': 'YES', 'GCC_WARN_UNUSED_VARIABLE': 'YES',
    'IPHONEOS_DEPLOYMENT_TARGET': '15.0', 'LOCALIZATION_PREFERS_STRING_CATALOGS': 'YES', 'MTL_FAST_MATH': 'YES', 'SDKROOT': 'iphoneos',
}
p_dbg = dict(warn, DEBUG_INFORMATION_FORMAT='dwarf', ENABLE_TESTABILITY='YES', GCC_DYNAMIC_NO_PIC='NO', GCC_OPTIMIZATION_LEVEL='0',
             GCC_PREPROCESSOR_DEFINITIONS=['DEBUG=1', '$(inherited)'], MTL_ENABLE_DEBUG_INFO='INCLUDE_SOURCE', ONLY_ACTIVE_ARCH='YES',
             SWIFT_ACTIVE_COMPILATION_CONDITIONS='DEBUG $(inherited)', SWIFT_OPTIMIZATION_LEVEL='-Onone')
p_rel = dict(warn, DEBUG_INFORMATION_FORMAT='dwarf-with-dsym', ENABLE_NS_ASSERTIONS='NO', MTL_ENABLE_DEBUG_INFO='NO',
             SWIFT_COMPILATION_MODE='wholemodule', VALIDATE_PRODUCT='YES')
tgt = {
    'ASSETCATALOG_COMPILER_APPICON_NAME': 'AppIcon', 'ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME': 'AccentColor',
    'CODE_SIGN_STYLE': 'Automatic', 'CURRENT_PROJECT_VERSION': '1', 'DEVELOPMENT_TEAM': '', 'ENABLE_PREVIEWS': 'NO',
    'GENERATE_INFOPLIST_FILE': 'NO', 'INFOPLIST_FILE': NAME + '/Info.plist', 'IPHONEOS_DEPLOYMENT_TARGET': '15.0',
    'LD_RUNPATH_SEARCH_PATHS': ['$(inherited)', '@executable_path/Frameworks'], 'MARKETING_VERSION': '1.0',
    'PRODUCT_BUNDLE_IDENTIFIER': BUNDLE_ID, 'PRODUCT_NAME': '$(TARGET_NAME)', 'SUPPORTED_PLATFORMS': 'iphoneos iphonesimulator',
    'SUPPORTS_MACCATALYST': 'NO', 'SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD': 'NO', 'SUPPORTS_XR_DESIGNED_FOR_IPHONE_IPAD': 'NO',
    'SWIFT_EMIT_LOC_STRINGS': 'YES', 'SWIFT_VERSION': '5.0', 'TARGETED_DEVICE_FAMILY': '1,2',
}
def cfg(i, name, d): return '\t\t%s /* %s */ = {\n\t\t\tisa = XCBuildConfiguration;\n\t\t\tbuildSettings = {\n%s\n\t\t\t};\n\t\t\tname = %s;\n\t\t};\n' % (I[i], name, settings(d), name)

L = []
L.append('// !$*UTF8*$!\n{\n\tarchiveVersion = 1;\n\tclasses = {\n\t};\n\tobjectVersion = 56;\n\tobjects = {\n')
L.append('\n/* Begin PBXBuildFile section */\n')
for f in SWIFT: L.append('\t\t%s /* %s in Sources */ = {isa = PBXBuildFile; fileRef = %s /* %s */; };\n' % (I['bf_' + f], f, I['fr_' + f], f))
for k, f in [('assets', 'Assets.xcassets'), ('game', 'Game'), ('priv', 'PrivacyInfo.xcprivacy')]:
    L.append('\t\t%s /* %s in Resources */ = {isa = PBXBuildFile; fileRef = %s /* %s */; };\n' % (I['bf_' + k], f, I['fr_' + k], f))
L.append('/* End PBXBuildFile section */\n\n/* Begin PBXFileReference section */\n')
L.append('\t\t%s /* %s.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = %s.app; sourceTree = BUILT_PRODUCTS_DIR; };\n' % (I['fr_app'], NAME, NAME))
for f in SWIFT: L.append('\t\t%s /* %s */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = %s; sourceTree = "<group>"; };\n' % (I['fr_' + f], f, f))
L.append('\t\t%s /* Assets.xcassets */ = {isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; };\n' % I['fr_assets'])
L.append('\t\t%s /* Game */ = {isa = PBXFileReference; lastKnownFileType = folder; path = Game; sourceTree = "<group>"; };\n' % I['fr_game'])
L.append('\t\t%s /* Info.plist */ = {isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; };\n' % I['fr_plist'])
L.append('\t\t%s /* PrivacyInfo.xcprivacy */ = {isa = PBXFileReference; lastKnownFileType = text.xml; path = PrivacyInfo.xcprivacy; sourceTree = "<group>"; };\n' % I['fr_priv'])
L.append('/* End PBXFileReference section */\n\n/* Begin PBXFrameworksBuildPhase section */\n')
L.append('\t\t%s /* Frameworks */ = {\n\t\t\tisa = PBXFrameworksBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t};\n' % I['fw'])
L.append('/* End PBXFrameworksBuildPhase section */\n\n/* Begin PBXGroup section */\n')
L.append('\t\t%s = {\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t%s /* %s */,\n\t\t\t\t%s /* Products */,\n\t\t\t);\n\t\t\tsourceTree = "<group>";\n\t\t};\n' % (I['g_main'], I['g_app'], NAME, I['g_prod']))
kids = [(I['fr_' + f], f) for f in SWIFT] + [(I['fr_game'], 'Game'), (I['fr_assets'], 'Assets.xcassets'), (I['fr_priv'], 'PrivacyInfo.xcprivacy'), (I['fr_plist'], 'Info.plist')]
L.append('\t\t%s /* %s */ = {\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n%s\t\t\t);\n\t\t\tpath = %s;\n\t\t\tsourceTree = "<group>";\n\t\t};\n' % (I['g_app'], NAME, ''.join('\t\t\t\t%s /* %s */,\n' % kv for kv in kids), NAME))
L.append('\t\t%s /* Products */ = {\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t\t%s /* %s.app */,\n\t\t\t);\n\t\t\tname = Products;\n\t\t\tsourceTree = "<group>";\n\t\t};\n' % (I['g_prod'], I['fr_app'], NAME))
L.append('/* End PBXGroup section */\n\n/* Begin PBXNativeTarget section */\n')
L.append('\t\t%s /* %s */ = {\n\t\t\tisa = PBXNativeTarget;\n\t\t\tbuildConfigurationList = %s /* Build configuration list for PBXNativeTarget "%s" */;\n\t\t\tbuildPhases = (\n\t\t\t\t%s /* Sources */,\n\t\t\t\t%s /* Frameworks */,\n\t\t\t\t%s /* Resources */,\n\t\t\t);\n\t\t\tbuildRules = (\n\t\t\t);\n\t\t\tdependencies = (\n\t\t\t);\n\t\t\tname = %s;\n\t\t\tproductName = %s;\n\t\t\tproductReference = %s /* %s.app */;\n\t\t\tproductType = "com.apple.product-type.application";\n\t\t};\n' % (I['target'], NAME, I['cl_t'], NAME, I['src'], I['fw'], I['res'], NAME, NAME, I['fr_app'], NAME))
L.append('/* End PBXNativeTarget section */\n\n/* Begin PBXProject section */\n')
L.append('\t\t%s /* Project object */ = {\n\t\t\tisa = PBXProject;\n\t\t\tattributes = {\n\t\t\t\tBuildIndependentTargetsInParallel = 1;\n\t\t\t\tLastSwiftUpdateCheck = 2600;\n\t\t\t\tLastUpgradeCheck = 2600;\n\t\t\t\tTargetAttributes = {\n\t\t\t\t\t%s = {\n\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;\n\t\t\t\t\t};\n\t\t\t\t};\n\t\t\t};\n\t\t\tbuildConfigurationList = %s /* Build configuration list for PBXProject "%s" */;\n\t\t\tcompatibilityVersion = "Xcode 14.0";\n\t\t\tdevelopmentRegion = en;\n\t\t\thasScannedForEncodings = 0;\n\t\t\tknownRegions = (\n\t\t\t\ten,\n\t\t\t\tBase,\n\t\t\t);\n\t\t\tmainGroup = %s;\n\t\t\tproductRefGroup = %s /* Products */;\n\t\t\tprojectDirPath = "";\n\t\t\tprojectRoot = "";\n\t\t\ttargets = (\n\t\t\t\t%s /* %s */,\n\t\t\t);\n\t\t};\n' % (I['proj'], I['target'], I['cl_p'], NAME, I['g_main'], I['g_prod'], I['target'], NAME))
L.append('/* End PBXProject section */\n\n/* Begin PBXResourcesBuildPhase section */\n')
L.append('\t\t%s /* Resources */ = {\n\t\t\tisa = PBXResourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n\t\t\t\t%s /* Assets.xcassets in Resources */,\n\t\t\t\t%s /* Game in Resources */,\n\t\t\t\t%s /* PrivacyInfo.xcprivacy in Resources */,\n\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t};\n' % (I['res'], I['bf_assets'], I['bf_game'], I['bf_priv']))
L.append('/* End PBXResourcesBuildPhase section */\n\n/* Begin PBXSourcesBuildPhase section */\n')
L.append('\t\t%s /* Sources */ = {\n\t\t\tisa = PBXSourcesBuildPhase;\n\t\t\tbuildActionMask = 2147483647;\n\t\t\tfiles = (\n%s\t\t\t);\n\t\t\trunOnlyForDeploymentPostprocessing = 0;\n\t\t};\n' % (I['src'], ''.join('\t\t\t\t%s /* %s in Sources */,\n' % (I['bf_' + f], f) for f in SWIFT)))
L.append('/* End PBXSourcesBuildPhase section */\n\n/* Begin XCBuildConfiguration section */\n')
L.append(cfg('p_dbg', 'Debug', p_dbg)); L.append(cfg('p_rel', 'Release', p_rel)); L.append(cfg('t_dbg', 'Debug', tgt)); L.append(cfg('t_rel', 'Release', tgt))
L.append('/* End XCBuildConfiguration section */\n\n/* Begin XCConfigurationList section */\n')
for i, what, a, b in [('cl_p', 'PBXProject', 'p_dbg', 'p_rel'), ('cl_t', 'PBXNativeTarget', 't_dbg', 't_rel')]:
    L.append('\t\t%s /* Build configuration list for %s "%s" */ = {\n\t\t\tisa = XCConfigurationList;\n\t\t\tbuildConfigurations = (\n\t\t\t\t%s /* Debug */,\n\t\t\t\t%s /* Release */,\n\t\t\t);\n\t\t\tdefaultConfigurationIsVisible = 0;\n\t\t\tdefaultConfigurationName = Release;\n\t\t};\n' % (I[i], what, NAME, I[a], I[b]))
L.append('/* End XCConfigurationList section */\n\t};\n\trootObject = %s /* Project object */;\n}\n' % I['proj'])
XP = OUT + '/' + NAME + '.xcodeproj'
os.makedirs(XP + '/project.xcworkspace/xcshareddata'); os.makedirs(XP + '/xcshareddata/xcschemes')
open(XP + '/project.pbxproj', 'w').write(''.join(L))
open(XP + '/project.xcworkspace/contents.xcworkspacedata', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<Workspace\n   version = "1.0">\n   <FileRef\n      location = "self:">\n   </FileRef>\n</Workspace>\n')
with open(XP + '/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist', 'wb') as f: plistlib.dump({'IDEDidComputeMac32BitWarning': True}, f)
ref = '''<BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "%s"
               BuildableName = "%s.app"
               BlueprintName = "%s"
               ReferencedContainer = "container:%s.xcodeproj">
            </BuildableReference>''' % (I['target'], NAME, NAME, NAME)
scheme = '''<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "2600"
   version = "1.7">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            %s
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES"
      shouldAutocreateTestPlan = "YES">
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         %s
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Release"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         %s
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>
''' % (ref, ref.replace('\n            ', '\n         '), ref.replace('\n            ', '\n         '))
open(XP + '/xcshareddata/xcschemes/' + NAME + '.xcscheme', 'w').write(scheme)
print(json.dumps({k: I[k] for k in ['proj', 'target']}), 'html bytes', os.path.getsize(GAME + '/index.html'))

shutil.copy(SP + '/ios/README.md', OUT + '/README.md')
