/**
* @description JSON store of size facet size members
*/
var facet_sizing = {
  /**
  * @description regular clothing sizes
  */
  regular_sizes: ['00','0','2','4','6','8','10','12','14','16'],
  /**
  * @description petite clothing sizes
  */  
  petite_sizes: ['00P','0P','2P','4P','6P','8P','10P','12P','14P','16P'],
  /**
  * @description tall clothing sizes
  */
  tall_sizes: [],
  /**
  * @description plus clothing sizes
  */  
  plus_sizes: ['18','20','22','24','26'],
  /**
  * @description no sizes - accessories and the like
  */  
  no_sizes: ['ONE SIZE'],
  /**
  * @description regular shoe sizes
  */
  regular_shoes: ['5','5.5','6','6.5','7','7.5','8','8.5','9','9.5','10','10.5','11','11.5','12','12.5','13','13.5','14'],
  /**
  * @description narrow shoe sizes
  */
  narrow_shoes: ['5N','5.5N','6N','6.5N','7N','7.5N','8N','8.5N','9N','9.5N','10N','10.5N','11N','11.5N','12N','12.5N','13N','13.5N','14N'],
  /**
  * @description wide shoe sizes
  */
  wide_shoes: ['5W','5.5W','6W','6.5W','7W','7.5W','8W','8.5W','9W','9.5W','10W','10.5W','11W','11.5W','12W','12.5W','13W','13.5W','14W'],
  /**
  * @description member groups for clothing sizes
  */
	clothing_members: {
    '00':{
      members: [{size:'00',name: '00'},{size:'XXS',name: 'XXS'},{size:'XX SMALL',name: 'XX SMALL'},{size:'XX-SMALL',name: 'XX-SMALL'},{size:'22', name: '22 <i>waistline</i>'},{size:'23',name:'23 <i>waistline</i>'},{size:'24',name:'24 <i>waistline</i>'}],
      sizes: ['00','XXS','XX SMALL', 'XX-SMALL','22','23','24']
    },
    '0':{
      members: [{size:'0',name: '0'},{size:'XS',name: 'XS'},{size:'X SMALL',name:'X SMALL'},{size:'X-SMALL',name:'X-SMALL'},{size:'24', name:'24 <i>waistline</i>'},{size:'25',name:'25 <i>waistline</i>'}],
      sizes: ['0','XS','X SMALL','X-SMALL','24','25']
    },
    '2':{
      members: [{size:'2',name: '2'},{size:'XS',name: 'XS'},{size:'XSMALL',name: 'XSMALL'},{size:'X-SMALL',name: 'X-SMALL'},{size:'26',name: '26 <i>waistline</i>'},{size:'32',name: '32 <i>EU</i>'}],
      sizes: ['2','XS','XSMALL','X-SMALL','26','32']
    },      
    '4':{
      members: [{size:'4',name: '4'},{size:'S',name: 'S'},{size:'SMALL',name:'SMALL'},{size:'27',name:'27 <i>waistline</i>'},{size:'34',name: '34 <i>EU</i>'}],
      sizes: ['4','S','SMALL','27','34']
    },      
    '6':{
      members: [{size:'6',name: '6'},{size:'S',name: 'S'},{size:'SMALL',name: 'SMALL'},{size:'28',name: '28 <i>waistline</i>'},{size:'36',name: '36 <i>EU</i>'}],
      sizes: ['6','S','SMALL','28','36']
    },      
    '8':{
      members: [{size:'8',name: '8'},{size:'M',name: 'M'},{size:'MEDIUM',name: 'MEDIUM'},{size:'29',name: '29 <i>waistline</i>'},{size:'38',name: '38 <i>EU</i>'}],
      sizes: ['8','M','MEDIUM','29','38']
    },      
    '10':{
      members: [{size:'10',name: '10'},{size:'M',name: 'M'},{size:'MEDIUM',name: 'MEDIUM'},{size:'30',name: '30 <i>waistline</i>'},{size:'40',name: '40 <i>EU</i>'}],
      sizes: ['10','M','MEDIUM','30','40']
    },      
    '12':{
      members: [{size:'12',name: '12'},{size:'L',name: 'L'},{size:'LARGE',name: 'LARGE'},{size:'0X',name: '0X'},{size:'31',name: '31 <i>waistline</i>'},{size:'42',name: '42 <i>EU</i>'}],
      sizes: ['12','L','LARGE','0X','31','42']
    },      
    '14':{
      members: [{size:'14',name: '14'},{size:'L',name: 'L'},{size:'LARGE',name: 'LARGE'},{size:'1X',name: '1X'},{size:'32',name: '32 <i>waistline</i>'},{size:'44',name: '44 <i>EU</i>'}],
      sizes: ['14','L','LARGE','1X','32','44']
    },      
    '16':{
      members: [{size:'16',name: '16'},{size:'XL',name: 'XL'},{size:'X LARGE',name: 'X LARGE'},{size:'X-LARGE',name: 'X-LARGE'},{size:'1X',name: '1X'},{size:'33',name: '33 <i>waistline</i>'},{size:'46',name: '46 <i>EU</i>'}],
      sizes: ['16','XL','X LARGE','X-LARGE','1X','33','46']
    },      
    '00P':{
      members: [{size:'00P',name: '00P'},{size:'PETITE X-SMALL',name: 'PETITE X-SMALL'},{size:'P/XS',name:'P/XS'}],
      sizes: ['00P','PETITE X-SMALL','P/XS']
    },      
    '0P':{
      members: [{size:'0P',name: '0P'},{size:'PETITE X-SMALL',name: 'PETITE X-SMALL'},{size:'P/XS',name:'P/XS'}],
      sizes: ['0P','PETITE X-SMALL','P/XS']
    },      
    '2P':{
      members: [{size:'2P',name: '2P'},{size:'PETITE SMALL',name: 'PETITE SMALL'},{size:'P/S',name:'P/S'}],
      sizes: ['2P','PETITE SMALL','P/S']
    },      
    '4P':{
      members: [{size:'4P',name: '4P'},{size:'PETITE SMALL',name: 'PETITE SMALL'},{size:'P/S',name:'P/S'}],
      sizes: ['4P','PETITE SMALL','P/S']
    },      
    '6P':{
      members: [{size:'6P',name: '6P'},{size:'PETITE SMALL',name: 'PETITE SMALL'},{size:'P/S',name:'P/S'}],
      sizes: ['6P','PETITE SMALL','P/S']
    },      
    '8P':{
      members: [{size:'8P',name: '8P'},{size:'PETITE MEDIUM',name: 'PETITE MEDIUM'},{size:'P/M',name:'P/M'}],
      sizes: ['8P','PETITE MEDIUM','P/M']
    },      
    '10P':{
      members: [{size:'10P',name: '10P'},{size:'PETITE MEDIUM',name: 'PETITE MEDIUM'},{size:'P/M',name:'P/M'}],
      sizes: ['10P','PETITE MEDIUM','P/M']
    },      
    '12P':{
      members: [{size:'12P',name: '12P'},{size:'PETITE LARGE',name: 'PETITE LARGE'},{size:'P/L',name:'P/L'}],
      sizes: ['12P','PETITE LARGE','P/L']
    },      
    '14P':{
      members: [{size:'14P',name: '14P'},{size:'PETITE LARGE',name: 'PETITE LARGE'},{size:'P/L',name:'P/L'}],
      sizes: ['14P','PETITE LARGE','P/L']
    },      
    '16P':{
      members: [{size:'16P',name: '16P'},{size:'PETITE X-LARGE',name: 'PETITE X-LARGE'},{size:'P/XL',name:'P/XL'}],
      sizes: ['16P','PETITE X-LARGE','P/XL']
    },      
    '18':{
      members: [{size:'18',name: '18'},{size:'XXL',name: 'XXL'},{size:'XX-LARGE',name: 'XX-LARGE'},{size:'2X',name: '2X'},{size:'34',name: '34 <i>waistline</i>'},{size:'48',name: '48 <i>EU</i>'}],
      sizes: ['18','XXL','XX-LARGE','2X','34','48']
    },      
    '20':{
      members: [{size:'20',name: '20'},{size:'2X',name: '2X'},{size:'50',name: '50 <i>EU</i>'}],
      sizes: ['20','2X','50']
    },      
    '22':{
      members: [{size:'22',name: '22'},{size:'3X',name: '3X'}],
      sizes: ['22','3X']
    },      
    '24':{
      members: [{size:'24',name: '24'},{size:'3X',name: '3X'}],
      sizes: ['24','3X']
    },      
    '26':{
      members: [{size:'26',name: '26'},{size:'4X',name: '4X'}],
      sizes: ['26','4X']
    },
    'ONE SIZE': {
      members: [{size:'ONE',name: 'ONE'},{size:'ONE SIZE',name: 'ONE SIZE'},{size: 'NO SIZE', name: 'NO SIZE'}],
      sizes: ['ONE','ONE SIZE','NO SIZE']        
    }    
  },
  /**
  * @description member groups for shoe sizes
  */  
  shoe_members: {
    '5':{
      members: [{size:'5',name: '5'},{size:'5M',name: '5M'},{size:'4.5',name: '4.5'},{size:'35',name: '35'},{size:'36',name: '36'}],
      sizes: ['5','5M','4.5','35','36']
    },
    '5.5':{
      members: [{size:'5.5',name: '5.5'},{size:'5.5M',name: '5.5M'},{size:'36',name: '36'}],
      sizes: ['5.5','5.5M','36']
    },
    '6':{
      members: [{size:'6',name: '6'},{size:'6M',name: '6M'},{size:'36',name: '36'},{size:'36(6)',name: '36(6)'},{size:'37',name: '37'}],
      sizes: ['6','6M','36','36(6)','37']
    },
    '6.5':{
      members: [{size:'6.5',name: '6.5'},{size:'6.5M',name: '6.5M'},{size:'37',name: '37'}],
      sizes: ['6.5','6.5M','37']
    },
    '7':{
      members: [{size:'7',name: '7'},{size:'7M',name: '7M'},{size:'37',name: '37'},{size:'37(7)',name: '37(7)'},{size:'38',name: '38'}],
      sizes: ['7','7M','37','37(7)','38']
    },
    '7.5':{
      members: [{size:'7.5',name: '7.5'},{size:'7.5M',name: '7.5M'},{size:'38',name: '38'}],
      sizes: ['7.5','7.5M','38']
    },
    '8':{
      members: [{size:'8',name: '8'},{size:'8M',name: '8M'},{size:'38',name: '38'},{size:'38(8)',name: '38(8)'},{size:'39',name: '39'}],
      sizes: ['8','8M','38','38(8)','39']
    },
    '8.5':{
      members: [{size:'8.5',name: '8.5'},{size:'8.5M',name: '8.5M'},{size:'39',name: '39'}],
      sizes: ['8.5','8.5M','39']
    },
    '9':{
      members: [{size:'9',name: '9'},{size:'9M',name: '9M'},{size:'39',name: '39'},{size:'39(9)',name: '39(9)'},{size:'40',name: '40'}],
      sizes: ['9','9M','39','39(9)','40']
    },
    '9.5':{
      members: [{size:'9.5',name: '9.5'},{size:'9.5M',name: '9.5M'},{size:'40',name: '40'}],
      sizes: ['9.5','9.5M','40']
    },
    '10':{
      members: [{size:'10',name: '10'},{size:'10M',name: '10M'},{size:'40',name: '40'},{size:'40(10)',name: '40(10)'},{size:'41',name: '41'}],
      sizes: ['10','10M','40','40(10)','41']
    },
    '10.5':{
      members: [{size:'10.5',name: '10.5'},{size:'10.5M',name: '10.5M'},{size:'41',name: '41'}],
      sizes: ['10.5','10.5M','41']
    },
    '11':{
      members: [{size:'11',name: '11'},{size:'11M',name: '11M'},{size:'41',name: '41'},{size:'41(11)',name: '41(11)'},{size:'42',name: '42'}],
      sizes: ['11','11M','41','41(11)','42']
    },
    '11.5':{
      members: [{size:'11.5',name: '11.5'},{size:'11.5M',name: '11.5M'},{size:'42',name: '42'}],
      sizes: ['11.5','11.5M','42']
    },
    '12':{
      members: [{size:'12',name: '12'},{size:'12M',name: '12M'},{size:'42',name: '42'},{size:'43',name: '43'}],
      sizes: ['12','12M','42','43']
    },
    '12.5':{
      members: [{size:'12.5',name: '12.5'},{size:'12.5M',name: '12.5M'}],
      sizes: ['12.5','12.5M']
    },
    '13':{
      members: [{size:'13',name: '13'},{size:'13M',name: '13M'}],
      sizes: ['13','13M']
    },
    '13.5':{
      members: [{size:'13.5',name: '13.5'},{size:'13.5M',name: '13.5M'}],
      sizes: ['13.5','13.5M']
    },
    '14':{
      members: [{size:'14',name: '14'},{size:'14M',name: '14M'}],
      sizes: ['14','14M']
    },
    '5N':{
      members: [{size:'5N',name: '5N'},{size:'4.5N',name: '4.5N'}],
      sizes: ['5N','4.5N']
    },
    '5.5N':{
      members: [{size:'5.5N',name: '5.5N'}],
      sizes: ['5.5N']
    },
    '6N':{
      members: [{size:'6N',name: '6N'}],
      sizes: ['6N']
    },
    '6.5N':{
      members: [{size:'6.5N',name: '6.5N'}],
      sizes: ['6.5N']
    },
    '7N':{
      members: [{size:'7N',name: '7N'}],
      sizes: ['7N']
    },
    '7.5N':{
      members: [{size:'7.5N',name: '7.5N'}],
      sizes: ['7.5N']
    },
    '8N':{
      members: [{size:'8N',name: '8N'}],
      sizes: ['8N']
    },
    '8.5N':{
      members: [{size:'8.5N',name: '8.5N'}],
      sizes: ['8.5N']
    },
    '9N':{
      members: [{size:'9N',name: '9N'}],
      sizes: ['9N']
    },
    '9.5N':{
      members: [{size:'9.5N',name: '9.5N'}],
      sizes: ['9.5N']
    },
    '10N':{
      members: [{size:'10N',name: '10N'}],
      sizes: ['10N']
    },
    '10.5N':{
      members: [{size:'10.5N',name: '10.5N'}],
      sizes: ['10.5N']
    },
    '11N':{
      members: [{size:'11N',name: '11N'}],
      sizes: ['11N']
    },
    '11.5N':{
      members: [{size:'11.5N',name: '11.5N'}],
      sizes: ['11.5N']
    },
    '12N':{
      members: [{size:'12N',name: '12N'}],
      sizes: ['12N']
    },
    '12.5N':{
      members: [{size:'12.5N',name: '12.5N'}],
      sizes: ['12.5N']
    },
    '13N':{
      members: [{size:'13N',name: '13N'}],
      sizes: ['13N']
    },
    '13.5N':{
      members: [{size:'13.5N',name: '13.5N'}],
      sizes: ['13.5N']
    },
    '14N':{
      members: [{size:'14N',name: '14N'}],
      sizes: ['14N']
    },
    '5W':{
      members: [{size:'5W',name: '5W'},{size:'4.5W',name: '4.5W'}],
      sizes: ['5W','4.5W']
    },
    '5.5W':{
      members: [{size:'5.5W',name: '5.5W'}],
      sizes: ['5.5W']
    },
    '6W':{
      members: [{size:'6W',name: '6W'}],
      sizes: ['6W']
    },
    '6.5W':{
      members: [{size:'6.5W',name: '6.5W'}],
      sizes: ['6.5W']
    },
    '7W':{
      members: [{size:'7W',name: '7W'}],
      sizes: ['7W']
    },
    '7.5W':{
      members: [{size:'7.5W',name: '7.5W'}],
      sizes: ['7.5W']
    },
    '8W':{
      members: [{size:'8W',name: '8W'}],
      sizes: ['8W']
    },
    '8.5W':{
      members: [{size:'8.5W',name: '8.5W'}],
      sizes: ['8.5W']
    },
    '9W':{
      members: [{size:'9W',name: '9W'}],
      sizes: ['9W']
    },
    '9.5W':{
      members: [{size:'9.5W',name: '9.5W'}],
      sizes: ['9.5W']
    },
    '10W':{
      members: [{size:'10W',name: '10W'}],
      sizes: ['10W']
    },
    '10.5W':{
      members: [{size:'10.5W',name: '10.5W'}],
      sizes: ['10.5W']
    },
    '11W':{
      members: [{size:'11W',name: '11W'}],
      sizes: ['11W']
    },
    '11.5W':{
      members: [{size:'11.5W',name: '11.5W'}],
      sizes: ['11.5W']
    },
    '12W':{
      members: [{size:'12W',name: '12W'}],
      sizes: ['12W']
    },
    '12.5W':{
      members: [{size:'12.5W',name: '12.5W'}],
      sizes: ['12.5W']
    },
    '13W':{
      members: [{size:'13W',name: '13W'}],
      sizes: ['13W']
    },
    '13.5W':{
      members: [{size:'13.5W',name: '13.5W'}],
      sizes: ['13.5W']
    },
    '14W':{
      members: [{size:'14W',name: '14W'}],
      sizes: ['14W']
    }            
  }
}