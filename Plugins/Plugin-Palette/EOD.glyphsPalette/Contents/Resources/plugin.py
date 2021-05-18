# encoding: utf-8

################################################################################
#
#	Explosive Ordnance Disposal
#	The Glyphs 3 Plugin from 3type
#
################################################################################

import gzip
import itertools
import os
import pickle
import random
import subprocess
import time

import objc
from GlyphsApp import (UPDATEINTERFACE, Glyphs, GSComponent,
                       GSEditViewController, GSGlyph, GSLayer, GSNode, GSPath)
from GlyphsApp.plugins import PalettePlugin


class EOD(PalettePlugin):
    '''
    ============================================================================
    objc IBOutlet Zone
    ============================================================================
    '''

    dialog = objc.IBOutlet()

    textFieldTargetZi = objc.IBOutlet()
    textFieldTargetZiFormulaType = objc.IBOutlet()
    textFieldPartAAmount = objc.IBOutlet()
    textFieldPartBAmount = objc.IBOutlet()
    textFieldProgress = objc.IBOutlet()
    textFieldNextHero = objc.IBOutlet()
    textFieldPartNameNote = objc.IBOutlet()

    checkBoxFormulaType = objc.IBOutlet()
    checkBoxDoneUniOnly = objc.IBOutlet()
    checkBoxFormulaDeepDown = objc.IBOutlet()

    progBarProgress = objc.IBOutlet()

    uniListPopupButton = objc.IBOutlet()
    heroAmountPopupButton = objc.IBOutlet()
    progPercentPopupButton = objc.IBOutlet()
    idsDataPopupButton = objc.IBOutlet()

    '''
	============================================================================
	objc IBAction Zone
	============================================================================
	'''

    @objc.IBAction
    def forgePartsButton_(self, sender):
        '''
        Find all the formula parts and call out. If _parts.xxx glyph is empty,
        copy form the done Zi.
        '''
        time_start = time.time()
        font = Glyphs.font
        thisUniList = [glyph.unicode for glyph in self.thisGlyphs()]

        if not thisUniList:
            return

        sumDict = {}
        partNameStr = ''

        for glyphUni in thisUniList:
            if glyphUni in self.idsDict.keys():
                formula = self.getFormula(glyphUni)
                # layerWidth = self.getHanWidth()
                partNameDict = self.getPartNameDict(formula)

                # partNameStr = ''
                for partName, noteList in partNameDict.items():
                    sumDict[partName] = sumDict.get(partName, 0) + 1

                    # _part.u8F66-LR get 8F66
                    rootName = partName.removeprefix(
                        '_part.u').split('-', 1)[0]
                    partNameStr = partNameStr + '/' + partName + ' '

                    if not font.glyphs[partName]:
                        font.glyphs.append(GSGlyph(partName))
                        if font.glyphs[rootName]:
                            font.glyphs[partName] = font.glyphs[rootName].copy()
                        else:
                            for master in font.masters:
                                layer = font.glyphs[partName].layers[master.id]
                                layer.shapes.append(self.getBombComponent())
                                layer.width = self.getHanWidth()

                        userData_partNameNote = '部件字符：%s \n生成于：【 %s 】 \n结构型：%s' % (noteList[0],
                                                                                   self.zi(glyphUni), noteList[1])
                        font.glyphs[partName].userData['EOD_partNameNote'] = userData_partNameNote

            else:
                continue
        if font.currentTab:
            font.currentTab.text = partNameStr + self.zi(thisUniList[0])
            font.currentTab.textCursor = len(font.currentTab.layers) - 1

        print('='*40, '\n部件查找计算用时：', round(time.time() - time_start, 2), 's')
        # print(sumDict)

        return

    @objc.IBAction
    def checkProgressButton_(self, sender):
        '''
        Check the done glyphs by totalStrokes.
        '''
        doneList = self.doneList(update=True)
        self.doneList(update=True, allList=True)

        font = Glyphs.font
        for xUni in doneList:
            font.glyphs[xUni].tags.addObject_('EOD_Done')
        textDone = Glyphs.localize({
            'en': 'Glyphs done: ',
            'zh': '已绘制：'})
        text = textDone+str(len(doneList))+' Unicode'
        self.textFieldProgress.setStringValue_(text)

        return

    @objc.IBAction
    def siblingButton_(self, sender):
        '''
        Call out all the sibling glyphs to play.
        '''
        time_start = time.time()

        font = Glyphs.font
        if (thisGlyphs := self.thisGlyphs()):
            thisGlyph = thisGlyphs[0]
        else:  # No selection
            return

        if not (thisGlyphUni := thisGlyph.unicode):  # No unicode glyphs
            return

        searchRange = []
        if self.checkBoxDoneUniOnly.intValue():
            searchRange = self.doneList()
        else:
            searchRange = self.doneList(allList=True)
        # print('='*40,'\nTime：',round(time.time() - time_start, 2),'s')

        if self.checkBoxFormulaType.intValue():
            formulaTypeList = []
            thisGlyphFormulaType = self.getFormula(thisGlyphUni)[0]
            for xUni in self.idsDict.keys():
                if thisGlyphFormulaType == self.getFormula(xUni)[0]:
                    formulaTypeList.append(xUni)
            searchRange = set(searchRange) & set(formulaTypeList)

        glyphZi = self.zi(thisGlyphUni)

        partListA = []
        partListB = []
        for xUni in searchRange:
            matchType, matchPart, matchNote = self.isSlibing(
                thisGlyphUni, xUni)
            if matchType in ['A', 'A-sub']:
                partListA.append(xUni)
            elif matchType in ['B', 'B-sub', 'C']:
                partListB.append(xUni)

        # print('='*20, '\n查询字:', glyphZi, '\n', '-'*20)

        def getRandomStr(xList, amount):
            rList = random.sample(xList, min(len(xList), amount))
            return ''.join(self.zi(x) for x in rList)

        partStrA = getRandomStr(
            partListA, self.textFieldPartAAmount.intValue())
        partStrB = getRandomStr(
            partListB, self.textFieldPartBAmount.intValue())
        # print('A侧部件:', partStrA)
        # print('B侧部件:', partStrB)

        tabText = partStrA + glyphZi + partStrB
        if font.currentTab:
            font.currentTab.text = tabText
        else:
            font.newTab(tabText)
        font.currentTab.textCursor = len(partStrA)
        Glyphs.defaults['com.the3type.EOD.siblingAmounts'] = [self.textFieldPartAAmount.intValue(),
                                                              self.textFieldPartBAmount.intValue()]

        # print('='*40,'\n姐妹字计算用时：',round(time.time() - time_start, 2),'s')

        return

    @objc.IBAction
    def nextHeroButton_(self, sender):
        '''
        Find your next Hero Glyph to help the most.
        '''
        font = Glyphs.font
        layerWidth = self.getHanWidth()

        uniListDict = {
            0: 'GB2312',
            1: 'Hanyi9169',
            2: 'Big5'	}
        uniListName = uniListDict[self.uniListPopupButton.indexOfSelectedItem()]

        searchRange = self.charSetDict[uniListName]
        print('Character set size: ', len(searchRange))
        doneList = self.doneList()
        print('Characters done: ', len(searchRange))

        heroAmount = self.heroAmountPopupButton.indexOfSelectedItem() + 1
        nextHeroList = self.nextHeroList(doneList, searchRange, heroAmount)

        nextHeroZiStr = ''
        for xUni in nextHeroList:
            nextHeroZiStr += self.zi(xUni)
            if not font.glyphs[xUni]:
                font.glyphs.append(GSGlyph(self.zi(xUni)))
            for layer in font.glyphs[xUni].layers:
                layer.width = layerWidth

        self.textFieldNextHero.setStringValue_(nextHeroZiStr)
        font.newTab(nextHeroZiStr)
        font.currentTab.textCursor = 0
        font.currentTab.textRange = 1

        return

    @objc.IBAction
    def loadIDSButton_(self, sender):
        '''
        Choose your IDS data.
        '''
        self.readPdata(self.idsDataPopupButton.indexOfSelectedItem())

        return

    '''
	============================================================================
	Glyphs-Plugin Zone
	============================================================================
	'''

    @objc.python_method
    def settings(self):
        self.name = Glyphs.localize({
            'en': 'Explosive Ordnance Disposal',
            'zh': '拆字小组',
        })

        self.loadNib('IBdialog', __file__)

        return

    @objc.python_method
    def start(self):
        Glyphs.addCallback(self.update, UPDATEINTERFACE)
        # Get ready for startup
        self.idsDict = {}
        self.charSetDict = {}
        self.lastActiveGlyph = GSGlyph()
        self.lastActiveTab = GSEditViewController
        self.runtimeDict = {}
        self.idsURLGithub = 'https://raw.githubusercontent.com/3type/EOD/master/datatool/output/idsDict.pdata'
        self.idsURLAlt = 'https://3type.cn/downloads/EOD/idsDict.pdata'
        # Load data
        self.readPdata()
        # UI setup
        siblingAmounts = Glyphs.defaults.get(
            'com.the3type.EOD.siblingAmounts', [3, 3])
        self.textFieldPartAAmount.setIntValue_(siblingAmounts[0])
        self.textFieldPartBAmount.setIntValue_(siblingAmounts[1])

        return

    @objc.python_method
    def __del__(self):
        Glyphs.removeCallback(self.update)
        return

    @objc.python_method
    def update(self, sender):
        font = Glyphs.font

        if not self.thisGlyphs():
            return

        thisGlyph = self.thisGlyphs()[0]
        if thisGlyph != self.lastActiveGlyph or font.currentTab != self.lastActiveTab:
            self.lastActiveGlyph = thisGlyph
            self.lastActiveTab = font.currentTab

        thisGlyphUni = thisGlyph.unicode
        if thisGlyphUni in self.idsDict.keys():
            targetZi = self.zi(thisGlyphUni)
            targetZiFormulaType = self.getFormula(thisGlyphUni)[0]
        else:
            targetZi = '⌀'
            targetZiFormulaType = '○'

        if thisGlyph.userData['EOD_partNameNote']:
            nameNote = thisGlyph.userData['EOD_partNameNote']
        elif thisGlyph.unicode:
            nameNote = '拆解结构式：\n'+self.getFormulaNote(thisGlyph.unicode,
                                                      deepDown=self.checkBoxFormulaDeepDown.intValue())
        else:
            nameNote = Glyphs.localize({
                'en': 'Glyph without Unicode',
                'zh': '无 Unicode 字符',
            })

        self.textFieldTargetZi.setStringValue_(targetZi)
        self.textFieldTargetZiFormulaType.setStringValue_(targetZiFormulaType)
        self.textFieldPartNameNote.setStringValue_(nameNote)

        return

    @objc.python_method
    def __file__(self):
        return __file__

    '''
	============================================================================
	EOD self.function Zone
	============================================================================
	'''

    @objc.python_method
    def thisGlyphs(self):
        font = Glyphs.font
        if font.currentTab:
            thisLayers = font.currentTab.selectedLayers
            if len(thisLayers) >= 1:
                thisGlyphList = [layer.parent for layer in thisLayers]
            else:
                thisGlyphList = []

        else:
            try:
                thisGlyphList = font.selection
            except:
                thisGlyphList = []

        return thisGlyphList

    @objc.python_method
    def zi(self, xUni):
        return chr(int(xUni, 16))

    @objc.python_method
    def uni(self, zi):
        return hex(ord(zi)).swapcase()[2:]

    @objc.python_method
    def getHanWidth(self):
        font = Glyphs.font
        layerWidth = 1000.0
        for x in font.customParameters:
            if x.name == 'Default Layer Width':
                layerWidth = float(x.value.removeprefix('han:'))
                if x.value.startswith('han:'):
                    break

        return layerWidth

    @objc.python_method
    def getFormula(self, xUni):
        if (xUniValue := self.idsDict.get(xUni)):
            return xUniValue.get('formula')
        else:
            zi = self.zi(xUni)
            return ['○', zi, zi]

    @objc.python_method
    def getFormulaNote(self, xUni, deepDown=False):
        if not self.idsDict:
            formulaNote = Glyphs.localize({
                'en': 'Please click the 「数据源」 tab to download or choose your data file',
                'zh': '首次使用，请点击「数据源」标签页，下载所需数据。',
            })
            return formulaNote

        def packList(xList, deep=False):
            outStr = ''
            for x in xList:
                # print(x)
                if isinstance(x, list):
                    outStr += '「%s」' % packList(x, deep)
                elif isinstance(x, str):
                    if len(x) > 1:  # For 'CDP-xxxxx'
                        outStr += '「%s」' % x
                    elif deep:  # Search the Zi again
                        formulaList = self.getFormula(self.uni(x))
                        if formulaList[0] == '○':
                            outStr += x
                        else:
                            outStr += '「%s」' % packList(formulaList, deep)
                    else:
                        outStr += x
            return outStr

        formulaList = self.getFormula(xUni)
        # print(formulaList)
        if formulaList[0] == '○':
            formulaNote = '「 %s 」' % formulaList[1]
        else:
            formulaNote = packList(formulaList, deepDown)
        return formulaNote

    @objc.python_method
    def getPartNameDict(self, formulaList):
        def cleanName(strOld):
            strNew = ''
            for x in strOld:
                if x.isalnum() or x in '-_':
                    pass
                else:
                    x = '_'
                strNew += x
            return strNew

        modelStrDict = {
            '⿰': [['-LR', '⿰ 左侧部', '⿰左'], ['-LR', '⿰ 右侧部']],
            '⿱': [['-AB', '⿱ 上侧部'], ['-AB', '⿱ 下侧部']],
            '⿴': [['-FS', '⿴ 全包围部'], ['-Si', '⿴ 被包围部']],
            '⿵': [['-SfA', '⿵ 上包围部'], ['-Si', '⿴ 被包围部']],
            '⿶': [['-SfB', '⿶ 下包围部'], ['-Si', '⿴ 被包围部']],
            '⿷': [['-SfL', '⿷ 左包围部'], ['-Si', '⿴ 被包围部']],
            '⿸': [['-SfAL', '⿸ 左上包围部'], ['-Si', '⿴ 被包围部']],
            '⿹': [['-SfAR', '⿹ 右上包围部'], ['-Si', '⿴ 被包围部']],
            '⿺': [['-SfBL', '⿺ 左下包围部'], ['-Si', '⿴ 被包围部']],
            '⿻': [['-XiX', '⿻ 交叠件'], ['-XiX', '⿻ 交叠件']],
            '⿲': [['-LR', '⿲ 左侧部'], ['-LR', '⿲ 中央部'], ['-LR', '⿲ 右侧部']],
            '⿳': [['-AB', '⿳ 上侧部'], ['-AB', '⿳ 中央部'], ['-AB', '⿳ 下侧部']]
        }
        modelSymbol = formulaList[0]
        if modelSymbol == '○':
            return {}

        modelList = modelStrDict[modelSymbol]
        partNameDict = {}
        for i, part in enumerate(formulaList[1:]):

            nameNote = modelList[i][1]
            if len(part) == 1:
                partFormulaList = self.getFormula(self.uni(part))
                if partFormulaList[0] == '○':
                    partNameStr = '_part.u' + self.uni(part) + modelList[i][0]
                    partNameDict[partNameStr] = [part, nameNote]
                else:
                    innerPartDict = self.getPartNameDict(partFormulaList)
                    for xName, xNote in innerPartDict.items():
                        nameNote = modelList[i][1] + ' ➤ 子结构：' + xNote[1]
                        innerPartDict[xName][1] = nameNote
                    partNameDict = innerPartDict | partNameDict

            elif isinstance(part, list):
                innerPartDict = self.getPartNameDict(part)
                for xName, xNote in innerPartDict.items():
                    nameNote = modelList[i][1] + ' ➤ 子结构：' + xNote[1]
                    innerPartDict[xName][1] = nameNote
                partNameDict = innerPartDict | partNameDict

            elif isinstance(part, str):
                partNameStr = '_part.' + cleanName(str(part)) + modelList[i][0]
                partNameDict[partNameStr] = [part, nameNote]

        return partNameDict

    @objc.python_method
    def nextHeroList(self, doneUniList, allUniList, amount=3):
        def cut2ModelDict(uniList):
            modelDict = {}
            for xUni in uniList:
                modelKey = self.getFormula(xUni)[0]
                if modelKey != '○':
                    modelDict.setdefault(modelKey, []).append(xUni)

            return modelDict

        time_start = time.time()
        self.progBarProgress.setDoubleValue_(0.0)

        idsSet = set(self.idsDict.keys())
        doneUniSet = set(doneUniList) & idsSet
        allUniSet = set(allUniList) & idsSet
        searhUniSet = allUniSet - doneUniSet

        nextUniSet = searhUniSet.copy()
        targetDict = cut2ModelDict(doneUniSet)

        for xUni in searhUniSet:
            modelKey = self.getFormula(xUni)[0]
            for yUni in targetDict.setdefault(modelKey, []):
                matchType, matchPart, matchNote = self.isSlibing(xUni, yUni)
                if matchType:
                    nextUniSet.discard(xUni)

        self.progBarProgress.setDoubleValue_(50.0)
        print('='*20, '\nPart1 Time：', round(time.time() - time_start, 2), 's')
        time_part1 = time.time()

        targetDict = cut2ModelDict(nextUniSet)
        xDict = {}
        for modelList in targetDict.values():
            for xUni, yUni in itertools.product(modelList, modelList):
                matchType, matchPart, matchNote = self.isSlibing(xUni, yUni)
                if matchType:
                    xDict[xUni] = xDict.get(xUni, 0) + 1

        allHeroLists = sorted(xDict.items(), key=lambda x: x[1], reverse=1)
        topHeroLists = allHeroLists[:amount]

        heroList = []
        for xUni, xCoverage in topHeroLists:
            heroList.append(xUni)

        self.progBarProgress.setDoubleValue_(100.0)
        print('='*20, '\nPart2 Time：', round(time.time() - time_part1, 2), 's')
        print('='*40, '\nTotal Time：', round(time.time() - time_start, 2), 's')

        return heroList

    @objc.python_method
    def doneList(self, update=False, allList=False):
        def getCompStrokes(glyph):
            if glyph:
                pathStrokes = len(glyph.layers[0].paths)
                if len(glyph.layers[0].components):
                    for comp in glyph.layers[0].components:
                        compStrokes = getCompStrokes(comp.component)
                else:
                    compStrokes = 0
                return pathStrokes + compStrokes
            return 0

        progPercentDict = {
            0: 0.7,
            1: 0.5,
            2: 0.3}
        progPercent = progPercentDict[self.progPercentPopupButton.indexOfSelectedItem(
        )]

        if allList:
            dataName = 'runtime_AllList'
        else:
            dataName = 'runtime_DoneList'

        listX = []
        if not update:
            listX = self.runtimeDict.get(dataName, [])
            if listX:
                return listX

        for glyph in Glyphs.font.glyphs:
            if allList:
                if glyph.unicode:
                    listX.append(glyph.unicode)
            else:
                totalStrokes = self.idsDict.get(
                    glyph.unicode, {'totalStrokes': 0}).get('totalStrokes')
                if totalStrokes <= 3:
                    targetStrokes = 1
                else:
                    targetStrokes = progPercent * totalStrokes

                doneStrokes = getCompStrokes(glyph)
                if doneStrokes >= targetStrokes and glyph.unicode:
                    listX.append(glyph.unicode)
                    glyph.tags.addObject_('EOD_Done')
                else:
                    glyph.tags.removeObject_('EOD_Done')
        self.runtimeDict[dataName] = listX

        return listX

    @objc.python_method
    def isSlibing(self, xUni, yUni):
        '''
        Check if the xUni/yUni formula match.
        '''
        slibingResult = [None, None, '未匹配']
        xGet, yGet = self.getFormula(xUni), self.getFormula(yUni)

        xA, xB = xGet[1], xGet[2]
        yA, yB = yGet[1], yGet[2]

        # A-Side match
        if xA == yA:
            slibingResult = ['A', xA, 'A侧 完全匹配：' + str(xA)]
        # B-Side match
        elif xB == yB:
            slibingResult = ['B', xB, 'B侧 完全匹配：' + str(xB)]
        # A-Side sub part match
        elif (isinstance(xA, list)
                and isinstance(yA, list)):
            if len(xA) == len(yA):
                if xA[0:2] == yA[0:2] or xA[0:3:2] == yA[0:3:2]:
                    slibingResult = ['A-sub', xA, 'A侧 子结构匹配：' + str(xA)]
        # B-Side sub part match
        elif (isinstance(xB, list)
                and isinstance(yB, list)):
            if len(xB) == len(yB):
                if xB[0:2] == yB[0:2] or xB[0:3:2] == yB[0:3:2]:
                    slibingResult = ['B-sub', xB, 'B侧 子结构匹配：' + str(xB)]
        # C-Side match for 3in1
        elif len(xGet) > 3 and xGet[-1] == yGet[-1]:
            xC = xGet[-1]
            slibingResult = ['C', xC, 'C侧 完全匹配：' + str(xC)]

        return slibingResult

    @objc.python_method
    def readPdata(self, option=0):
        '''
        Load or download the pdata file.
        '''
        workDir = os.path.dirname(__file__)
        with gzip.open(workDir+'/dataset/charSetDict.pdata', 'rb') as fin:
            self.charSetDict = pickle.load(fin)
            print('EOD charSetDict Ready')

        idsDataPath = workDir+'/dataset/idsDict.pdata'
        if option:
            if option == 1:
                url = self.idsURLGithub
            elif option == 2:
                url = self.idsURLAlt
            else:
                return

            print('EOD idsData Target URL:%s' % url)
            try:
                # Call curl to download https url
                subprocess.call(['curl', '--output', idsDataPath, url])
                localtime = time.asctime(time.localtime(time.time()))
                print('EOD idsDict downloaded @ ', localtime)
            except:
                print('EOD ERROR: curl failed!')

        try:
            with gzip.open(workDir+'/dataset/idsDict.pdata', 'rb') as fin:
                self.idsDict = pickle.load(fin)
            print('EOD idsDict{} Readed')
        except:
            print('EOD idsDict data missing or broken.\nPlease Try Again.')

        return

    @objc.python_method
    def getBombComponent(self):
        aBomb = '_EOD.aBomb'
        font = Glyphs.font
        if not font.glyphs[aBomb]:
            workDir = os.path.dirname(__file__)
            with gzip.open(workDir+'/dataset/aBombList.pdata', 'rb') as fin:
                aBombNodeList = pickle.load(fin)

            shapeList = []
            for path in aBombNodeList:
                newPath = GSPath()
                for node in path:
                    newNode = GSNode()
                    newNode.position = (node[0], node[1])
                    newNode.type = node[2]
                    newPath.nodes.append(newNode)
                newPath.closed = True
                shapeList.append(newPath)

            font.glyphs.append(GSGlyph(aBomb))
            aBombGlyph = font.glyphs[aBomb]
            for layer in aBombGlyph.layers:
                layer.width = self.getHanWidth()
                layer.shapes = shapeList

        return GSComponent(font.glyphs[aBomb], (0, 0))
