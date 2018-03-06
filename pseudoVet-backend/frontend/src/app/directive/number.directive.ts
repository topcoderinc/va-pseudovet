import { Directive, ElementRef, HostListener, OnInit } from '@angular/core';
import { NumberPipe } from '../pipe/number.pipe';

@Directive({
  selector: '[appNumber]'
})
export class NumberDirective implements OnInit {
  private el: any;

  constructor (private elementRef: ElementRef,
               private numberPipe: NumberPipe) {
    this.el = this.elementRef.nativeElement;

  }

  ngOnInit () {
    this.el.value = this.numberPipe.transform(this.el.value);
  }

  @HostListener('focus', ['$event.target.value'])
  onFocus (value) {
    this.el.value = this.numberPipe.parse(value);
  }

  @HostListener('blur', ['$event.target.value'])
  onBlur (value) {
    this.el.value = this.numberPipe.transform(value);
  }


}
