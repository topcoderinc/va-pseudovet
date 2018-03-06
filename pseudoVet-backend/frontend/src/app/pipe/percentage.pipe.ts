import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'percentage'
})
export class PercentagePipe implements PipeTransform {

  transform (value: any, args?: any): any {
    value = (value || '').toString();
    value = value.replace(/\D/g, '');
    value = value === '' ? '0' : value;
    return value.indexOf('%') === -1 ? value + '%' : value;
  }

  parse (value: string): string {
    value = (value || '').toString();
    value = value.replace(/\D/g, '');
    value = value === '' ? '0' : value;
    return value.indexOf('%') === -1 ? value + '%' : value;
  }

}
