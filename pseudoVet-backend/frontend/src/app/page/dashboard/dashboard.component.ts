import { Component, OnInit } from '@angular/core';
import { DataService } from '../../services/data.service';
import { UtilService } from '../../services/util.service';
import { Router } from '@angular/router';
import { AppConfig } from '../../config';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  dashboardData: any = {};
  datasets: any = [];
  inProgressDatasets: any = [];
  deleteInProgress = false;
  deleteInProgressObj: any = {};
  deleteGenerated = false;
  deleteGeneratedObj: any = {};
  exportGenerated = false;
  exportGeneratedObj: any = {};
  reGenerated = false;
  reGeneratedObj: any = {};
  menu = [
    { name: 'Dashboard', url: '/dashboard', subname: '', active: true },
    { name: 'Create configuration', url: '/configuration/create', subname: '' },
    { name: 'Load configuration', url: '/load', subname: '' }
  ];

  constructor (private dataService: DataService,
               private toastr: ToastrService,
               private router: Router) {
    this.fetchDatasets();
  }

  /**
   * fetch datasets
   */
  fetchDatasets () {
    this.dataService.getDatasets().then(res => {
      this.datasets = res;
    }).catch(err => {
      console.error(err);
      this.toastr.error(err.message);
    });
  }

  /**
   * Remove items form in progress
   * @param index - item index
   */
  removeInProgressItem (index) {
    this.deleteInProgress = true;
    const name = this.dashboardData.inprogress[index].name;
    const progress = this.dashboardData.inprogress[index].progress;
    this.deleteInProgressObj = {
      index,
      name,
      progress
    };
  }

  /**
   * Remove In Progress Item
   */
  removeInProgress () {
    this.dashboardData.inprogress.splice(this.deleteInProgressObj.index, 1);
    this.deleteInProgress = false;
  }

  /**
   * remove items from generated
   * @param index - item index
   */
  removeGeneratedItem (index) {
    this.deleteGenerated = true;
    const dataset = this.datasets[index];
    const configObj = dataset.configuration;
    this.deleteGeneratedObj = {
      index,
      name: configObj.title,
      text: UtilService.getDescriptionByBackendConfig(configObj)
    };
  }

  /**
   * on delete generated item
   */
  onRemoveGeneratedItem () {
    this.dataService.deleteDatasetByTitle(this.deleteGeneratedObj.name).then(res => {
      this.datasets.splice(this.deleteGeneratedObj.index, 1);
      this.deleteGenerated = false;
      this.toastr.success('Dataset remove succeed');
    }).catch(err => {
      console.error(err);
      this.toastr.error(err.message);
    });
  }

  /**
   * Export generated item
   * @param index - item index
   */
  exportGeneratedItem (index) {
    this.exportGenerated = true;
    const name = this.dashboardData.generated[index].name;
    let text = this.dashboardData.generated[index].demographics;
    const split = text.split('/');
    split[1] = split[1] + ' patients';
    split[2] = split[2] + ' male-female ratio';
    text = split.join('/');
    this.exportGeneratedObj = {
      index,
      name,
      text
    };
  }

  /**
   * Regenerate Items
   * @param index - item index
   */
  reGeneratedItem (index) {
    this.reGenerated = true;
    const dataset = this.datasets[index];
    const configObj = dataset.configuration;
    this.reGeneratedObj = {
      index,
      name: configObj.title,
      text: UtilService.getDescriptionByBackendConfig(configObj)
    };
  }

  /**
   * on re generated button click
   */
  onReGeneratedDataset () {
    this.dataService.generateDatasets(this.reGeneratedObj.name).then(res => {
      this.reGenerated = false;
      this.reGeneratedObj = null;
      this.fetchDatasets();
      this.toastr.success('Dataset reGenerate succeed');
    }).catch(err => {
      console.error(err);
      this.toastr.error(err.message);
    });
  }

  /**
   * on dataset edit configuration
   */
  onConfigurationEditClick (index) {
    const configObj = this.datasets[index].configuration;
    localStorage.setItem(AppConfig.EDIT_CONFIG_KEY, JSON.stringify(configObj));
    this.router.navigate(['/configuration/dashboard/edit']);
  }


  ngOnInit () {
  }

}
