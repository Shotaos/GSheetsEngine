mainUI = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>644</width>
    <height>627</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>SearchEngine</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <property name="sizePolicy">
    <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
     <horstretch>0</horstretch>
     <verstretch>0</verstretch>
    </sizepolicy>
   </property>
   <layout class="QHBoxLayout" name="horizontalLayout_4">
    <item>
     <layout class="QGridLayout" name="gridLayout">
      <property name="sizeConstraint">
       <enum>QLayout::SetDefaultConstraint</enum>
      </property>
      <property name="verticalSpacing">
       <number>12</number>
      </property>
      <item row="0" column="0">
       <widget class="QGroupBox" name="search_group">
        <property name="sizePolicy">
         <sizepolicy hsizetype="Expanding" vsizetype="Preferred">
          <horstretch>0</horstretch>
          <verstretch>0</verstretch>
         </sizepolicy>
        </property>
        <property name="minimumSize">
         <size>
          <width>0</width>
          <height>0</height>
         </size>
        </property>
        <property name="contextMenuPolicy">
         <enum>Qt::NoContextMenu</enum>
        </property>
        <property name="title">
         <string/>
        </property>
        <property name="alignment">
         <set>Qt::AlignCenter</set>
        </property>
        <property name="flat">
         <bool>false</bool>
        </property>
        <property name="checkable">
         <bool>false</bool>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout_2">
         <item>
          <widget class="QLineEdit" name="search_line_input">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
             <horstretch>3</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777215</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="baseSize">
            <size>
             <width>0</width>
             <height>6</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QPushButton" name="search_button">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
             <horstretch>1</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777215</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="text">
            <string>Search</string>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QScrollArea" name="exclude_sheets">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Fixed">
             <horstretch>8</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="widgetResizable">
            <bool>true</bool>
           </property>
           <widget class="QWidget" name="scrollAreaWidgetContents">
            <property name="geometry">
             <rect>
              <x>0</x>
              <y>0</y>
              <width>367</width>
              <height>60</height>
             </rect>
            </property>
            <layout class="QHBoxLayout" name="horizontalLayout_5"/>
           </widget>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
      <item row="2" column="0">
       <widget class="QGroupBox" name="groupBox">
        <property name="title">
         <string/>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout_3">
         <item>
          <widget class="QTableWidget" name="main_table">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
             <horstretch>0</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="minimumSize">
            <size>
             <width>600</width>
             <height>0</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="contextMenuPolicy">
            <enum>Qt::CustomContextMenu</enum>
           </property>
           <property name="layoutDirection">
            <enum>Qt::LeftToRight</enum>
           </property>
           <property name="autoFillBackground">
            <bool>false</bool>
           </property>
           <property name="alternatingRowColors">
            <bool>true</bool>
           </property>
           <property name="gridStyle">
            <enum>Qt::SolidLine</enum>
           </property>
           <property name="sortingEnabled">
            <bool>true</bool>
           </property>
           <attribute name="horizontalHeaderCascadingSectionResizes">
            <bool>false</bool>
           </attribute>
           <attribute name="verticalHeaderCascadingSectionResizes">
            <bool>false</bool>
           </attribute>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
      <item row="1" column="0">
       <widget class="QGroupBox" name="add_record_group">
        <property name="sizePolicy">
         <sizepolicy hsizetype="Expanding" vsizetype="Preferred">
          <horstretch>0</horstretch>
          <verstretch>0</verstretch>
         </sizepolicy>
        </property>
        <property name="contextMenuPolicy">
         <enum>Qt::NoContextMenu</enum>
        </property>
        <property name="title">
         <string/>
        </property>
        <layout class="QHBoxLayout" name="horizontalLayout">
         <item>
          <widget class="QLabel" name="topic_label">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>1</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777215</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="sizeIncrement">
            <size>
             <width>0</width>
             <height>0</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="layoutDirection">
            <enum>Qt::LeftToRight</enum>
           </property>
           <property name="text">
            <string>Topic:</string>
           </property>
           <property name="scaledContents">
            <bool>false</bool>
           </property>
           <property name="alignment">
            <set>Qt::AlignCenter</set>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QComboBox" name="add_topic_dropdown">
           <property name="enabled">
            <bool>true</bool>
           </property>
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>2</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="minimumSize">
            <size>
             <width>0</width>
             <height>0</height>
            </size>
           </property>
           <property name="maximumSize">
            <size>
             <width>150</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="contextMenuPolicy">
            <enum>Qt::NoContextMenu</enum>
           </property>
           <item>
            <property name="text">
             <string>Blender</string>
            </property>
           </item>
          </widget>
         </item>
         <item>
          <widget class="QLabel" name="category_label">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>1</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777215</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="sizeIncrement">
            <size>
             <width>0</width>
             <height>0</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="layoutDirection">
            <enum>Qt::LeftToRight</enum>
           </property>
           <property name="text">
            <string>Category:</string>
           </property>
           <property name="scaledContents">
            <bool>false</bool>
           </property>
           <property name="alignment">
            <set>Qt::AlignCenter</set>
           </property>
           <property name="wordWrap">
            <bool>false</bool>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QLineEdit" name="category_line">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>2</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777193</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="contextMenuPolicy">
            <enum>Qt::NoContextMenu</enum>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QLabel" name="title_label">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>1</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777215</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="sizeIncrement">
            <size>
             <width>0</width>
             <height>0</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="layoutDirection">
            <enum>Qt::LeftToRight</enum>
           </property>
           <property name="text">
            <string>Title:</string>
           </property>
           <property name="scaledContents">
            <bool>false</bool>
           </property>
           <property name="alignment">
            <set>Qt::AlignCenter</set>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QLineEdit" name="title_line">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>4</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="maximumSize">
            <size>
             <width>16777193</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="contextMenuPolicy">
            <enum>Qt::NoContextMenu</enum>
           </property>
          </widget>
         </item>
         <item>
          <widget class="QPushButton" name="add_record">
           <property name="sizePolicy">
            <sizepolicy hsizetype="Preferred" vsizetype="Preferred">
             <horstretch>2</horstretch>
             <verstretch>0</verstretch>
            </sizepolicy>
           </property>
           <property name="minimumSize">
            <size>
             <width>100</width>
             <height>0</height>
            </size>
           </property>
           <property name="maximumSize">
            <size>
             <width>200</width>
             <height>16777215</height>
            </size>
           </property>
           <property name="font">
            <font>
             <pointsize>10</pointsize>
            </font>
           </property>
           <property name="contextMenuPolicy">
            <enum>Qt::NoContextMenu</enum>
           </property>
           <property name="text">
            <string>Add Record</string>
           </property>
          </widget>
         </item>
        </layout>
       </widget>
      </item>
      <item row="3" column="0">
       <layout class="QHBoxLayout" name="horizontalLayout_6">
        <property name="leftMargin">
         <number>5</number>
        </property>
        <property name="topMargin">
         <number>5</number>
        </property>
        <property name="rightMargin">
         <number>5</number>
        </property>
        <property name="bottomMargin">
         <number>5</number>
        </property>
        <item>
         <widget class="QLabel" name="log_text">
          <property name="maximumSize">
           <size>
            <width>700</width>
            <height>60</height>
           </size>
          </property>
          <property name="text">
           <string/>
          </property>
         </widget>
        </item>
        <item>
         <spacer name="horizontalSpacer">
          <property name="orientation">
           <enum>Qt::Horizontal</enum>
          </property>
          <property name="sizeHint" stdset="0">
           <size>
            <width>40</width>
            <height>20</height>
           </size>
          </property>
         </spacer>
        </item>
        <item>
         <widget class="QPushButton" name="settings_button">
          <property name="text">
           <string>Settings</string>
          </property>
         </widget>
        </item>
       </layout>
      </item>
     </layout>
    </item>
   </layout>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>'''

settingsUI = '''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Dialog</class>
 <widget class="QDialog" name="Dialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>469</width>
    <height>413</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Dialog</string>
  </property>
  <widget class="QDialogButtonBox" name="okButton">
   <property name="geometry">
    <rect>
     <x>370</x>
     <y>20</y>
     <width>81</width>
     <height>241</height>
    </rect>
   </property>
   <property name="orientation">
    <enum>Qt::Vertical</enum>
   </property>
   <property name="standardButtons">
    <set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set>
   </property>
  </widget>
  <widget class="QLabel" name="label">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>30</y>
     <width>67</width>
     <height>19</height>
    </rect>
   </property>
   <property name="text">
    <string>Sheet ID</string>
   </property>
  </widget>
  <widget class="QLineEdit" name="sheetId">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>60</y>
     <width>301</width>
     <height>27</height>
    </rect>
   </property>
  </widget>
  <widget class="QLabel" name="label_3">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>120</y>
     <width>131</width>
     <height>19</height>
    </rect>
   </property>
   <property name="text">
    <string>Exclude Sheets</string>
   </property>
  </widget>
  <widget class="QWidget" name="gridLayoutWidget">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>150</y>
     <width>431</width>
     <height>241</height>
    </rect>
   </property>
   <layout class="QGridLayout" name="exclude_sheets"/>
  </widget>
 </widget>
 <resources/>
 <connections>
  <connection>
   <sender>okButton</sender>
   <signal>accepted()</signal>
   <receiver>Dialog</receiver>
   <slot>accept()</slot>
   <hints>
    <hint type="sourcelabel">
     <x>248</x>
     <y>254</y>
    </hint>
    <hint type="destinationlabel">
     <x>157</x>
     <y>274</y>
    </hint>
   </hints>
  </connection>
  <connection>
   <sender>okButton</sender>
   <signal>rejected()</signal>
   <receiver>Dialog</receiver>
   <slot>reject()</slot>
   <hints>
    <hint type="sourcelabel">
     <x>316</x>
     <y>260</y>
    </hint>
    <hint type="destinationlabel">
     <x>286</x>
     <y>274</y>
    </hint>
   </hints>
  </connection>
 </connections>
</ui>'''