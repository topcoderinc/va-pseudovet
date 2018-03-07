import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { DataService } from '../../services/data.service';
import { map, find, indexOf, isUndefined, filter, each, cloneDeep } from 'lodash';
import { saveAs } from 'file-saver/FileSaver';
import { AppConfig } from '../../config';
import { UtilService } from '../../services/util.service';
import { ToastrService } from 'ngx-toastr';
import { NgProgress } from '@ngx-progressbar/core';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss']
})
export class ConfigurationComponent implements OnInit {
  configurationData: any = { // empty configuration
    title: '',
    patients: '',
    male: '',
    female: '',
    configurations: [],
    conditions: [],
    war: '',
    warStart: { d: '', m: '', y: '' },
    warEnd: { d: '', m: '', y: '' },
    selectedConfigurations: [],
    selectedConditions: [],
  };
  configurationSave = false;
  exportModal = false;
  title = 'EDIT DATASET';
  selectedTab = 1;
  create = true;
  editConfigObj: any = {};

  /* delete place holders */
  deleteModal = false;
  deleteType = '';
  deleteIcd10Code = '';
  deleteName = '';

  /* gender place holders */
  genderModal = false;
  genderName = '';
  genderType = '';
  gender = '';
  age = '';
  menu = [];
  dashboard = true;

  /* backend data */
  warEars = [];
  morbidities = [];

  constructor (private route: ActivatedRoute,
               private router: Router,
               private toastr: ToastrService,
               private ngProgress: NgProgress,
               private dataService: DataService) {
    this.create = route.snapshot.params['type'] === 'create';

    this.dashboard = true;
    if (!this.create) { // edit mode
      this.dashboard = route.snapshot.params['page'] === 'dashboard';
      this.title = this.dashboard ? 'EDIT DATASET' : 'EDIT DATASET CONFIGURATION';
      this.menu = [
        {
          name: 'Dashboard' + (this.dashboard ? ':' : ''),
          url: '/dashboard',
          subname: (this.dashboard ? 'Edit' : ''),
          active: this.dashboard
        },
        { name: 'Create configuration', url: '/configuration/create', subname: '', active: false },
        {
          name: 'Load configuration' + (!this.dashboard ? ':' : ''),
          url: '/load',
          subname: (!this.dashboard ? 'Edit' : ''),
          active: !this.dashboard
        }
      ];

      try {
        const configObj = JSON.parse(localStorage.getItem(AppConfig.EDIT_CONFIG_KEY));
        this.editConfigObj = configObj;
        this.configurationData = this.convertToFrontendConfiguration(configObj);
      } catch (e) {
        this.toastr.error(e.message);
      }
    } else {
      this.title = 'CREATE NEW DATASET CONFIGURATION';
      this.menu = [
        { name: 'Dashboard', url: '/dashboard', subname: '' },
        { name: 'Create configuration', url: '/configuration/create', subname: '', active: true },
        { name: 'Load configuration', url: '/load', subname: '' }
      ];
    }

    // fetch wars
    dataService.getWarEras().then(res => {
      this.warEars = res;
      if (this.configurationData.war) {
        this.onWarSelected(this.configurationData.war);
      }
    }).catch(err => {
      console.error(err);
      this.toastr.error(err.message);
    });
  }

  ngOnInit () {
  }


  /**
   * on war selected
   * @param value the war code
   */
  onWarSelected (value) {
    this.configurationData.war = value;
    const war = this.warEars.find(w => w.warEra === value);
    if (!!war) {
      this.configurationData.warStart = this.getDMYByTimeString(war.warEraStartDate);
      this.configurationData.warEnd = this.getDMYByTimeString(war.warEraEndDate);
    } else {
      this.configurationData.warStart = { d: '', m: '', y: '' };
      this.configurationData.warEnd = { d: '', m: '', y: '' };
    }
  }

  /**
   * get war start d/m/y by time string from backend
   * @param timeStr the time string
   * @return {any}
   */
  getDMYByTimeString (timeStr) {
    try {
      const t = new Date(timeStr);
      return { d: t.getUTCDate(), m: t.getUTCMonth() + 1, y: t.getUTCFullYear() };
    } catch (e) {
      console.error(e);
      return { d: '', m: '', y: '' };
    }
  }


  /**
   * validate step 01
   * @returns {boolean}
   */
  step1Validation () {
    let error = false;
    const mandatory = ['title', 'patients', 'male', 'female', 'war'];
    each(mandatory, (label) => {
      if (this.configurationData[label] === '') {
        error = true;
      }
    });

    const timeMandatory = ['d', 'm', 'y'];
    each(timeMandatory, (label) => {
      if (this.configurationData.warStart[label] === '' || this.configurationData.warEnd[label] === '') {
        error = true;
      }
    });
    return error;
  }


  /**
   * Validate step 2
   * @returns {boolean}
   */
  step2Validation () {
    return this.configurationData.configurations.length === 0;
  }

  /**
   * Validate Step 3
   * @returns {boolean}
   */
  step3Validation () {
    return false;
  }

  /**
   * on next button click
   */
  onNextClick () {
    this.selectedTab = this.selectedTab + 1;
    if (this.selectedTab === 2) { // this mean switch to MORBIDITY
      this.dataService.getMorbiditiesByWarName(this.configurationData.war).then(res => {
        this.morbidities = res as any;
      }).catch(err => {
        console.error(err);
        this.toastr.error(err.message);
      });
    }
  }

  /**
   * Add new configuration items
   * @param items
   */
  onAddConfiguration (items: [any]) {
    const selectedOptions = this.configurationData.configurations;
    const removed = [];
    for (let i = 0; i < selectedOptions.length; i++) {
      const index = items.findIndex(item => item.icd10Code === selectedOptions[i].icd10Code);
      if (index === -1) {
        removed.push(selectedOptions[i].icd10Code);
      }
    }

    this.configurationData.configurations = filter(this.configurationData.configurations,
      (item) => removed.findIndex(r => r === item.icd10Code) === -1);

    for (let i = 0; i < items.length; i++) {
      const index = selectedOptions.find(option => option.icd10Code === items[i].icd10Code);
      if (isUndefined(index)) {
        this.configurationData.configurations.push({
          'icd10Code': items[i].icd10Code,
          'name': items[i].name,
          'diagnosis': '0%',
          'acquires': '0%',
          'profiles': '0',
          'gender': 'None',
          'age': ''
        });
      }
    }
  }

  /**
   * Add new Condition items
   * @param items
   */
  onAddCondition (items) {
    const selectedOptions = this.configurationData.conditions;
    const removed = [];
    for (let i = 0; i < selectedOptions.length; i++) {
      const index = indexOf(items, selectedOptions[i].name);
      if (index === -1) {
        removed.push(selectedOptions[i].name);
      }
    }

    this.configurationData.conditions = filter(this.configurationData.conditions, (item) => indexOf(removed, item.name) === -1);
    for (let i = 0; i < items.length; i++) {
      const index = find(selectedOptions, { 'name': items[i] });
      if (isUndefined(index)) {
        this.configurationData.conditions.push({
          'name': items[i],
          'diagnosis': '0%',
          'acquires': '0%',
          'profiles': '0',
          'gender': 'None'
        });
      }
    }
  }

  /**
   * Delete item form configuration/conditions
   * @param code - the code
   * @param name - name of the item
   * @param dType - type [configuration/conditions]
   */
  deleteItems (code, name, dType) {
    this.deleteModal = true;
    this.deleteType = dType;
    this.deleteIcd10Code = code;
    this.deleteName = name;
  }


  /**
   * Remove selected item
   */
  removeItem () {
    this.deleteModal = false;
    this.configurationData[this.deleteType] =
      filter(this.configurationData[this.deleteType], (item) => item.icd10Code !== this.deleteIcd10Code);

    const items = [];
    each(this.configurationData[this.deleteType], (item) => {
      items.push({ icd10Code: item.icd10Code, name: item.name });
    });

    if (this.deleteType === 'conditions') {
      this.configurationData.selectedConditions = items;
    } else {
      this.configurationData.selectedConfigurations = items;
    }
  }

  /**
   * Change gender
   * @param gender - gender [Male/Female/None]
   */
  changeGender (gender) {
    this.gender = gender;
  }

  /**
   * Edit gender
   * @param item - the item
   * @param gType - type [configuration/conditions]
   */
  editGender (item, gType) {
    this.genderModal = true;
    this.genderName = item.icd10Code + '-' + item.name;
    this.genderType = gType;
    this.gender = item.gender;
    this.age = item.age;
  }

  /**
   * Update Gender
   */
  updateExcludes () {
    this.genderModal = false;
    const gender = this.gender;
    const name = this.genderName;
    this.configurationData[this.genderType] = map(this.configurationData[this.genderType],
      (item) => {
        if (item.icd10Code + '-' + item.name === name) {
          item.gender = gender;
          item.age = this.age;
        }
        return item;
      });
  }

  /**
   * on export button click
   */
  onExportClick () {
    this.exportModal = true;
    const configObject = this.convertToBackendConfiguration(this.configurationData);
    const blob = new Blob([JSON.stringify(configObject, null, 2)], { type: 'text/plain' });
    saveAs(blob, configObject.title + '.json');
  }

  /**
   * on save button clicked
   */
  onSaveClick () {
    const configObject = this.convertToBackendConfiguration(this.configurationData);
    this.dataService.createOrUpdatedatasetConfiguration(configObject).then(res => {
      if (this.dashboard) {
        this.router.navigate(['/dashboard']);
      } else {
        this.configurationSave = true;
      }
      this.toastr.success('Configuration save succeed');
    }).catch(err => {
      console.error(err);
      this.toastr.error(err.message);
    });
  }

  /**
   * on generate button click
   */
  onGenerateClick () {
    const configObject = this.convertToBackendConfiguration(this.configurationData);
    this.dataService.createOrUpdatedatasetConfiguration(configObject).then(configRes => {
      this.toastr.info('Configuration create/update succeed, start generate dataset...');
      this.startGenerateDataset();
    }).catch(configErr => {
      console.error(configErr);
      this.toastr.error(configErr.message);
    });
  }

  /**
   * start generate dataset by title
   */
  startGenerateDataset () {
    this.ngProgress.start();
    this.dataService.generateDatasets(this.configurationData.title).then(res => {
      this.toastr.success('Dataset generate succeed');
      this.ngProgress.completed();
    }).catch(err => {
      console.error(err);
      this.ngProgress.completed();
      this.toastr.error(err.message);
    });
  }

  /**
   * frontend configuration convert to backend configuration, then send this config object to server
   * @param frontendConfig the frontend config object
   * @return the backend config object
   */
  convertToBackendConfiguration (frontendConfig) {
    const configObject = {
      title: frontendConfig.title,
      numberOfPatients: parseInt(frontendConfig.patients, 10),
      maleRatio: parseFloat(frontendConfig.male),
      femaleRatio: parseFloat(frontendConfig.female),
      morbiditiesData: frontendConfig.configurations.map(m => ({
        icd10Code: m.icd10Code,
        name: m.name,
        exclusionRules: UtilService.getExclusionsByItem(m),
        numberOfEncounters: parseFloat(m.profiles),
        percentOfPopulationWithDiagnosisRisk: parseFloat(m.diagnosis.substr(0, m.diagnosis.length - 1)),
        percentOfProbabilityToAcquireDiagnosis: parseFloat(m.acquires.substr(0, m.acquires.length - 1)),
      })),
      warEra: this.warEars.find(w => w.warEra === frontendConfig.war),
      year: frontendConfig.year
    };
    if (!configObject.year) {
      configObject.year = new Date().getUTCFullYear();
    }
    return configObject;
  }

  getDialogDescription () {
    const configObj = this.configurationData;
    return `${configObj.war} / ${configObj.patients.toLocaleString()} patients / ${
      configObj.male}:${configObj.female} male-female ratio"`;
  }

  /**
   * convert backend config object to frontend config object, so that frontend can use directly
   * @param backendConfig the backend config object
   * @return frontend config object
   */
  convertToFrontendConfiguration (backendConfig) {
    return { // empty configuration
      title: backendConfig.title,
      patients: backendConfig.numberOfPatients,
      male: backendConfig.maleRatio,
      female: backendConfig.femaleRatio,
      configurations: backendConfig.morbiditiesData.map(m => ({
        icd10Code: m.icd10Code,
        name: m.name,
        age: UtilService.getAgeFromExclusions(m.exclusionRules),
        gender: UtilService.getGenderFromExclusions(m.exclusionRules),
        diagnosis: m.percentOfPopulationWithDiagnosisRisk + '%',
        acquires: m.percentOfProbabilityToAcquireDiagnosis + '%',
        profiles: m.numberOfEncounters,
      })),
      conditions: [],
      war: backendConfig.warEra.warEra,
      warStart: this.getDMYByTimeString(backendConfig.warEra.warEraStartDate),
      warEnd: this.getDMYByTimeString(backendConfig.warEra.warEraEndDate),
      selectedConfigurations: backendConfig.morbiditiesData.map(m => ({
        icd10Code: m.icd10Code,
        name: m.name,
      })),
      selectedConditions: [],
    };
  }

  /**
   * on input male/female value change, radio sum should be 100
   * @param value the changed value
   * @param type the value type, male/female
   */
  onRadioChange (value, type) {
    let v = parseInt(value, 10);
    if (!isNaN(v)) {
      if (v > 100) {
        v = 100;
        this.configurationData[type] = `${v}`;
      }
      this.configurationData[type === 'male' ? 'female' : 'male'] = 100 - v;
    }
  }
}
